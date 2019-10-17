# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Workflow/2-umap'))
	
except:
	pass

#%%
import pandas as pd
import numpy as np
import fcsparser as fcs
import umap
import sys

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
## UMAP
# Perform umap analysis, but let's first create and concatenate any files that we will be suing as input
# Input: Output from step 1, originally cytobank non-transformed .txt exports
# We do lose support for vs files (vSNE on cytobank?)
### Step 1: Concatenate all files
#### Consider:
#- Do you need to downsample each condition to the same cell number?

#%% Function to concatenate all files
def concatenate_fcs(folder_name):
    filenames_no_arcsinh = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]
    no_arc = pd.DataFrame()
    file_list =[] 
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for file in filenames_no_arcsinh:
        fcounter += 1
        df = pd.read_csv(f"{folder_name}/{file}", sep = '\t')
        df["file_origin"] = str(fcounter)+" | "+ file # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        no_arc = no_arc.append(df, ignore_index=True)
    return no_arc
#%% Perform concatenation
# set up working directory
#   files to be concatenated are kept in a subfolder called 'files' in the 
# current working folder (i.e. current_dir/files)
# umap is generated using arcsinh transformed data
#   the non-arcsinh transformed data is used for data uploading back into Cytobank after umap info is incorporated

folder_name = "input"

no_arc = concatenate_fcs(folder_name)

#%% Arcsinh transform the data
def arcsinh_transf(cofactor):
    arc = no_arc.iloc[:,:-1] #leave out the last column ('file_origin')
    #Select only the columns containing the markers (as they start with a number for the isotope)
    cols = [x for x in arc.columns if x[0].isdigit()]
    #Apply the arcsinh only to those columns (don't want to change time or any other)
    arc = arc.apply(lambda x: np.arcsinh(x/cofactor) if x.name in cols else x)
    # put back the 'file_origin' column to the arcsinh-transformed data
    arc["file_origin"] = no_arc["file_origin"]
    return arc, cols

#%% Perform transformation

#Literature recommends cofactor of 5 for cytof data
cofactor = 5

arc, cols = arcsinh_transf(cofactor)
#Storing marker columns for later use in UMAP

#%% [markdown]
# ### Step 2: Make umaps
# # #### Step 2.1: Setup UMAP parameters

#%%
# UMAP PARAMETERS 
nn = "no-norm"
rs = 2.0
nsr = 8
n = 15
m = 0.1
comp = 2
d = "euclidean"

# include here the information that would be helpful to understand the umaps
info_run = "fig-1_demo"

#%% [markdown]
# #### Step 2.2: Define the markers used for UMAP calculation
#%% Read them from a .csv file in ./input
#Sanity check
marker_files = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".csv")]
if len(marker_files) != 1:
    sys.exit("ERROR: There should be ONE .csv file with the markers to use in ./input!")

marker_file = pd.read_csv(f"{folder_name}/{marker_files[0]}", header=None)

#Get markers flagged for use
def identify_markers(marker_file):
    markers_umap = marker_file.loc[marker_file[1] == "Y", [0]].values.tolist()
    markers_umap = [item for sublist in markers_umap for item in sublist] #Flatten list
    return markers_umap

#%%
# OLD CODE CAN ALL BE DEPRECATED. LEVERAGE INSTEAD THE COLS FOUND EARLIER: group columns of the dataframe based on the type of measurement
#standard_columns = ["Event #", "Time", "Event_length", "Center", "Offset", "Width", "Residual","tSNE1", "tSNE2", "Unnamed: 0", "Unnamed: 0.1", "barcode_num", "barcode_name", "barcode_whole_name", "file_origin"]

not_markers_cols = [column for column in arc.columns if column not in cols]
all_markers_cols = cols.copy()

#cytobank_vs_cols = [column for column in arc.columns if "(v)" in column] # this is valid only when the data is exported from viSNE experiments

# define the v's for umap calculation (vs_markers_cols)
not_these = [] # columns to be excluded for umap calculation
vs_markers_cols = identify_markers(marker_file)
no_vs_markers_cols = [column for column in all_markers_cols if column not in vs_markers_cols]

# keep the columns ('v's) needed for umap calculation (all_together_vs_marks)
all_together_vs_marks = arc[vs_markers_cols].copy()

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

#COMMENT#

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


