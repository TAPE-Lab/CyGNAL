# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), '../../../../../../var/folders/hw/fqkcybzs3gq_bksy6wfr534m0000gr/T'))
	print(os.getcwd())
except:
	pass

#%%
import pandas as pd
import numpy as np
import fcsparser as fcs
import umap

import os
import shutil
# import time
import random
from sklearn import preprocessing
from collections import defaultdict
from scipy.stats import zscore

import dask.dataframe as dd

import holoviews as hv
from IPython.core.interactiveshell import InteractiveShell

import warnings
warnings.filterwarnings('ignore')

# print(umap.__version__)

# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"

#%% [markdown]
# ### Step 1: Concatenate all files
# #### Consider:
# - Do you need to downsample each condition to the same cell number?

#%%
# set up working directory
# files to be concatenated are kept in a subfolder called 'files' in the current working folder (i.e. current_dir/files)
# both arcsinh and non-arcsinh transformed files need to be exported from Cytobank as txt files
# umap is generated using arcsinh transformed data
# the non-arcsinh transformed data is used for data uploading back into Cytobank after umap info is incorporated

folder_name = "input"

# create the list of fcs files to be concatenated

filenames_no_arcsinh = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]

# the arcsinh and non-arcsinh data files have to be of the SAME order! 
# or otherwise the umap info will not be appended to the cells correctly
# filenames_no_arcsinh_order = [f.split("_arcsinh.txt")[0] for f in filenames_arcsinh]
# filenames_no_arcsinh = [f"{f}_no-arcsinh.txt" for f in filenames_no_arcsinh_order]

# filenames_arcsinh
filenames_no_arcsinh


#%%
# concatenating input files
# add a new column of 'file_origin' that will be used to separate each file after umap calculation

# arc = pd.DataFrame()
# for file in filenames_arcsinh:
#     df = pd.read_csv(f"{folder_name}/{file}", sep="\t")
#     df["file_origin"] = file
#     arc = arc.append(df, ignore_index=True)
#     print(f"arc.shape = ({arc.shape[0]}, {arc.shape[1]})")
    
no_arc = pd.DataFrame()
for file in filenames_no_arcsinh:
    df = pd.read_csv(f"{folder_name}/{file}", sep = '\t')
    df["file_origin"] = file
    no_arc = no_arc.append(df, ignore_index=True)
    print(f"no_arc.shape = ({no_arc.shape[0]}, {no_arc.shape[1]})")

# arcsinh transformation; leave out the last column ('file_origin')
cofactor = 5  
arc = no_arc.iloc[:,:-1].apply(lambda x: np.arcsinh(x/cofactor))

# put back the 'file_origin' column to the arcsinh-transformed data
arc["file_origin"] = no_arc["file_origin"]

arc.head()
no_arc.head()

#%% [markdown]
# ### Step 2: Make umaps
#%% [markdown]
# #### Step 2.1: Setup UMAP parameters

#%%
# UMAP PARAMETERS 
nn = "no-norm"
rs = 2.0
nsr = 8
n = 15
m = 0.1
comp = 2
d = "euclidean"


#%%
######
# include here the information that would be helpful to understand the umaps
######

info_run = "fig-1_demo"

#%% [markdown]
# #### Step 2.2: Define the markers used for UMAP calculation

#%%
# group columns of the dataframe based on the type of measurement
standard_columns = ["Event #", "Time", "Event_length", "Center", "Offset", "Width", "Residual","tSNE1", "tSNE2", "Unnamed: 0", "Unnamed: 0.1", "barcode_num", "barcode_name", "barcode_whole_name", "file_origin"]
not_markers_cols = [column for column in arc.columns if column in standard_columns]
all_markers_cols = [column for column in arc.columns if column not in standard_columns]
cytobank_vs_cols = [column for column in arc.columns if "(v)" in column] # this is valid only when the data is exported from viSNE experiments

# define the v's for umap calculation (vs_markers_cols)
not_these = [] # columns to be excluded for umap calculation
yes_these = [c for c in arc.columns if 'RB' in c or 'Caspase' in c or 'pHH3' in c or 'IdU' in c or
             'LRIG1' in c or 'Lysozyme' in c or 'CHGA' in c or 'DCAMKL1' in c or 'CLCA1' in c or 'FABP1' in c or 'CD44' in c] # columns to be included for umap calculation         

vs_markers_cols = [column for column in cytobank_vs_cols if column not in not_these] + yes_these # or choose the v's to be used from scratch
no_vs_markers_cols = [column for column in all_markers_cols if column not in vs_markers_cols]

# keep the columns ('v's) needed for umap calculation (all_together_vs_marks)
all_together_vs_marks = arc[vs_markers_cols].copy()
# all_together_vs_marks.head()

print(f"Markers used for UMAP calculation: \n")
print('\n'.join([m for m in all_together_vs_marks]))
print(f"\n Number of markers used: {len(all_together_vs_marks.columns)}")

#%% [markdown]
# ##### Optional: z-score transformation

#%%
# z-score transformation (for the Organoid Methods Paper, only applied to supplementary figure 1)
all_together_vs_marks = all_together_vs_marks.apply(zscore)
all_together_vs_marks.head()

#%% [markdown]
# #### Step 2.3 UMAP Calculation

#%%
# umap embedding calculation; result saved in a pandas dataframe
# the names of the umap info columns are also defined here
umap_emb = pd.DataFrame(umap.UMAP(n_neighbors=n, min_dist=m, metric=d, n_components=comp, repulsion_strength=rs, negative_sample_rate=nsr).fit_transform(all_together_vs_marks), 
                        columns=[f"umap_{info_run}_norm={nn}_rs={rs}_nsr={nsr}_n={n}_m={m}_{d}_1",f"umap_{info_run}_norm={nn}_rs={rs}_nsr={nsr}_n={n}_m={m}_{d}_2"])


#%%
# append umap info columns

no_arc[f"umap_{info_run}_norm={nn}_rs={rs}_nsr={nsr}_n={n}_m={m}_{d}_1"] = umap_emb[f"umap_{info_run}_norm={nn}_rs={rs}_nsr={nsr}_n={n}_m={m}_{d}_1"]
no_arc[f"umap_{info_run}_norm={nn}_rs={rs}_nsr={nsr}_n={n}_m={m}_{d}_2"] = umap_emb[f"umap_{info_run}_norm={nn}_rs={rs}_nsr={nsr}_n={n}_m={m}_{d}_2"]

no_arc.head()
umap_emb.head()

no_arc.tail()
umap_emb.tail()

#%% [markdown]
# ### Step 3: Get files ready for cytobank upload
# Note: You should use "no-arcsinh" when you want to convert the files to a Cytobank- and Scaffold- compatible format
#%% [markdown]
# #### Step 3.1: Format the column names

#%%
# reformat/clean-up the column names for umap info

data = no_arc.copy()
[c for c in list(data.columns) if "umap" in c]

["".join("_n_".join("d_".join("".join(c.split("norm=")).split("comp=2_min_dist=")).split("n_neighbors=")).split("metric=")) for c in list(data.columns) if "umap" in c]
p = ["".join("_n_".join("d_".join("".join(c.split("norm=")).split("comp=2_min_dist=")).split("n_neighbors=")).split("metric=")) for c in list(data.columns) if "umap" in c]

col_change = dict(zip([c for c in list(data.columns) if "umap" in c], p))
col_change

data.rename(columns = col_change, inplace = True)


#%%
# rename the columns for Cytobank
# this step has something to do with Cytobank's configuration of Channel Name/Reagent
# alternatively, leave the renaming to the final clean-step (use 'python_panel_editing_tool.ipynb')

cytobank_naming = {}

parenthesis = [c for c in list(data.columns) if "_(" in c]
vs = [c for c in parenthesis if " (v)" in c]
not_vs = [c for c in parenthesis if c not in vs]
stay_same = [c for c in list(data.columns) if c not in parenthesis]

# if len(parenthesis + stay_same) != len(list(peli.columns)):
#     print("THERE ARE SOME DUPLICATES, COLUMN NAMES THAT ARE IN MORE THAN ONE CATEGORIES\n")

for c in vs:
    names = c.split(" (v)_(")
    channel_name = names[1][:-1]
    marker_reagent = names[0][:]
    cytobank_naming[c] = (f"{channel_name}__{marker_reagent}")

for c in not_vs:
    names = c.split("_(")
    channel_name = names[1][:-1]
    marker_reagent = names[0]
    cytobank_naming[c] = (f"{channel_name}__{marker_reagent}")

for c in stay_same:
    cytobank_naming[c] = (f"{c}__{c}")
    
data.rename(columns = cytobank_naming, inplace = True)
list(data.columns)

#%% [markdown]
# #### Step 3.2: Revolve the data into separtate conditions
# For the following steps, you need to enter the info for each sample manually

#%%
# display the list of files of origin
data["file_origin__file_origin"].unique()


#%%
# split the data into individual dataframes for each sample
id_data = data[data["file_origin__file_origin"]==f"id_no-arcsinh.txt"]
cd_data = data[data["file_origin__file_origin"]==f"cd_no-arcsinh.txt"]
iv_data = data[data["file_origin__file_origin"]==f"iv_no-arcsinh.txt"]
control_data = data[data["file_origin__file_origin"]==f"control_no-arcsinh.txt"]
cv_data = data[data["file_origin__file_origin"]==f"cv_no-arcsinh.txt"]
all_data = data.iloc[:,:].copy()


#%%
# generate a dictionary of dataframes for looping; n+1 files (each + all)
all_updated_dict = {}
all_updated_dict["id_data"] = id_data.iloc[:,:].copy()
all_updated_dict["cd_data"] = cd_data.iloc[:,:].copy()
all_updated_dict["iv_data"] = iv_data.iloc[:,:].copy()
all_updated_dict["control_data"] = control_data.iloc[:,:].copy()
all_updated_dict["cv_data"] = cv_data.iloc[:,:].copy()
all_updated_dict["all_data"] = all_data.iloc[:,:].copy()


#%%
# save the output; the index column needs to be dropped, or otherwise Cytobank will give error messages
for k, v in all_updated_dict.items():
    data_new = v.copy()
    name = k.split("_data")[0]
    data_new.to_csv(f"{name}_no-arcsinh_input-to-cytobank.txt", sep="\t", index = False)


#%%


