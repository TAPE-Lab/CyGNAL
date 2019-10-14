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
import fcsparser
import pandas as pd
import numpy as np
import scprep
import os
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
from sklearn import preprocessing
from matplotlib.offsetbox import AnchoredText

import holoviews as hv
from IPython.core.interactiveshell import InteractiveShell
#%matplotlib inline


#%%
# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"


#%%
# parameter setup

cofactor = 5
k = 10
n_bins = 20
n_mesh = 3
plot = True
return_drevi = False


#%%
# set up working directory (emd_dir)
# files to be analysed (compare_from and compare_to) are kept in a subfolder called 'all_for_emd' in the current working folder (i.e. current_dir/all_for_emd)

current_dir = os.getcwd()
emd_dir = os.path.join(current_dir, "all_for_emd")

current_dir
emd_dir


#%%
# set up the files to be analysed (compare_from and compare_to)
# change the name of the 'compare_to‘ fcs file if needed

base_fcs_file = "Ungated.fcs" # the fcs file everything compares to (denominator)

emd_files = [file for file in os.listdir(emd_dir) if file.endswith(".fcs")]
compare_from = [f for f in emd_files if f != base_fcs_file]

compare_to = [base_fcs_file]

compare_from
compare_to


#%%
# create new folders to save the output of the script: plots and info

# plot_dir = os.path.join(current_dir, "plots")
# os.makedirs(plot_dir)

info_dir = os.path.join(current_dir, "info")

if os.path.isdir(info_dir) == False:
    os.makedirs(info_dir) 


#%%
# calculate emd and sign the emd score by the difference of median between compare_from and compare_to

def emd_arc(data_from_arc, data_to_arc, marker, normalization):
    
    df_info_dict[f"median_{normalization}_arc_compare_from"] = data_from_arc[marker].median()

    df_info_dict[f"median_{normalization}_arc_compare_to"] = data_to_arc[marker].median()
    
    df_info_dict[f"median_diff_{normalization}_arc_compare_from_vs_to"] = data_from_arc[marker].median() - data_to_arc[marker].median()
    
    if (data_from_arc[marker].median() - data_to_arc[marker].median()) >= 0:
        emd_arc = scprep.stats.EMD(data_from_arc[m], data_to_arc[m])
    if (data_from_arc[marker].median() - data_to_arc[marker].median()) < 0:
        emd_arc = -scprep.stats.EMD(data_from_arc[m], data_to_arc[m])
    
    # compile the sample info
    df_info_dict[f"EMD_{normalization}_arc"] = emd_arc
    
    return(emd_arc)


#%%
# convert the dictionary of normalised compare_from/compare_to data into lists for emd calculation

def create_lists(d):
#     arc_all_norm = [f for f in list(d.keys()) if "arc" in f]
#     arc_z_score = [f for f in list(d.keys()) if "arc" in f and "z_score" in f]
#     arc_zero_mean_shift = [f for f in list(d.keys()) if "arc" in f and "zero_mean_shift" in f]
#     arc_min_max = [f for f in list(d.keys()) if "arc" in f and "min_max" in f]
    arc_no_norm = [f for f in list(d.keys()) if "arc" in f and "no_norm" in f]

#     no_arc_all_norm = [f for f in list(d.keys()) if f not in arc_all_norm]
#     no_arc_z_score = [f for f in list(d.keys()) if f not in arc_all_norm and "z_score" in f]
#     no_arc_zero_mean_shift = [f for f in list(d.keys()) if f not in arc_all_norm and "zero_mean_shift" in f]
#     no_arc_min_max = [f for f in list(d.keys()) if f not in arc_all_norm and "min_max" in f]
#     no_arc_no_norm = [f for f in list(d.keys()) if f not in arc_all_norm and "no_norm" in f]
    
#     return(arc_all_norm, arc_z_score, arc_zero_mean_shift, arc_min_max, arc_no_norm, no_arc_all_norm, no_arc_z_score, no_arc_zero_mean_shift, no_arc_min_max, no_arc_no_norm)
    return(arc_no_norm)


#%%
# create a dataframe to store the dremi result
df_info = pd.DataFrame()

# get the info for the denominator
compare_to_file = base_fcs_file
compare_to_type = compare_to_file.split(".fcs")[0]

# read in the metadata of the compare_to fcs file and perform arcsinh transformation
path_to = os.path.join(emd_dir, compare_to_file)
meta_to, data_to = fcsparser.parse(path_to, reformat_meta=True)
data_to_arc = data_to.iloc[:,:].apply(lambda x: np.arcsinh(x/cofactor))

for compare_from_file in compare_from:
    
    compare_from_type = compare_from_file.split(".fcs")[0]
    
    # read in the metadata of the compare_to fcs file and perform arcsinh transformation
    path_from = os.path.join(emd_dir, compare_from_file)
    meta_from, data_from = fcsparser.parse(path_from, reformat_meta = True)
    data_from_arc = data_from.iloc[:,:].apply(lambda x: np.arcsinh(x/cofactor))
    
    # compile the sample info for the compare_from file
    df_info_dict = {}
    df_info_dict["compare_from"] = f"{compare_from_type}"
    df_info_dict["compare_to"] = f"{compare_to_type}"
    
    # create a dictionary (d) to store the normalised compare_from/compare_to data (arc/non-arc)
    d = {}
    
    d["data_no_norm_from_arc"] = data_from_arc
    d["data_no_norm_to_arc"] = data_to_arc
    
    # set up the list of markers for which emd scores are going to be calculated (all markers except for umaps)
    markers = [m for m in list(data_from.columns) if "_" in m and "Barcode" not in m and "Beads" not in m]
    
    (arc_no_norm) = create_lists(d)
    
    for m in markers:
        if m in list(data_to.columns):
            # compile the sample info
            df_info_dict["marker"] = m
            
            # calculate signed emd; the sample info is added to the dictionary within the emd function
            (emd_no_norm_arc) = emd_arc(data_from_arc, data_to_arc, m, "no_norm")          
            arc_no_norm = [emd_no_norm_arc]
            
            df_info = df_info.append(df_info_dict, ignore_index = True) # save the info in the dict (df_info_dict) to a dataframe (df_info)   
            
        else:
            print("THE COMPARE_FROM AND COMPARE_TO PANELS DON'T MATCH")

# save info in the dataframe df_info to a txt file
df_info.to_csv(f"{info_dir}/info.txt", sep="\t")


#%%


