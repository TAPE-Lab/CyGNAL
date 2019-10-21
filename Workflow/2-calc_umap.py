#UMAP#
# No support for IP/Jupyter notebooks
import pandas as pd
import numpy as np
import umap
import sys
import os
from aux2_umap_functions import *
from aux_functions import concatenate_fcs

import warnings
warnings.filterwarnings('ignore')

## UMAP
# Perform umap analysis, but let's first create and concatenate any files that we will be suing as input
# Input: Output from step 1, originally cytobank non-transformed .txt exports
# We do lose support for vs files (vSNE on cytobank?)
### Step 1: Concatenate all files
#### Consider:
#- Do you need to downsample each condition to the same cell number?

#Perform concatenation
# set up working directory
#   files to be concatenated are kept in a subfolder called 'files' in the 
# current working folder (i.e. current_dir/files)
# umap is generated using arcsinh transformed data
#   the non-arcsinh transformed data is used for data uploading back into Cytobank after umap info is incorporated

folder_name = "input/2-umap"

no_arc, input_files = concatenate_fcs(folder_name)

#Perform transformation
#Literature recommends cofactor of 5 for cytof data
cofactor = 5

arc, cols = arcsinh_transf(cofactor, no_arc)
#Storing marker columns for later use in UMAP


# ### Step 2: Make umaps
# #### Step 2.1: Define the markers used for UMAP calculation
#Read them from a .csv file in ./input
#Sanity check
marker_files = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".csv")]
if len(marker_files) != 1:
    sys.exit("ERROR: There should be ONE .csv file with the markers to use in the input folder!")

marker_file = pd.read_csv(f"{folder_name}/{marker_files[0]}", header=None)


# OLD CODE CAN ALL BE DEPRECATED. LEVERAGE INSTEAD THE COLS FOUND EARLIER: group columns of the dataframe based on the type of measurement

not_markers_cols = [column for column in arc.columns if column not in cols]
all_markers_cols = cols.copy()


# define the v's for umap calculation (vs_markers_cols)
not_these = [] # columns to be excluded for umap calculation
vs_markers_cols = identify_markers(marker_file)
no_vs_markers_cols = [column for column in all_markers_cols if column not in vs_markers_cols]

# keep the columns ('v's) needed for umap calculation (all_together_vs_marks)
all_together_vs_marks = arc[vs_markers_cols].copy()

print(f"Markers used for UMAP calculation: \n")
print('\n'.join([m for m in all_together_vs_marks]))
print(f"\n Number of markers used: {len(all_together_vs_marks.columns)}")


# ##### Optional: z-score transformation

# Z-SCORE: Not used now, interactive inplementation on later stages of the pipeline
# z-score transformation (for the Organoid Methods Paper, only applied to supplementary figure 1)
# all_together_vs_marks.head()
# all_together_vs_marks = all_together_vs_marks.apply(zscore)
# all_together_vs_marks.head()


# #### Step 2.2: Define UMAP parameters
# UMAP PARAMETERS 
nn = "no-norm"
rs = 2.0
nsr = 8
n = 15
m = 0.1
comp = 2
d = "euclidean"
# include here the information that would be helpful to understand the umaps
info_run =  input("Write UMAP info run (using no spaces!): ")

umap_params = {"nn":nn, "rs":rs, "nsr":nsr, "n":n, "m":m, "comp":comp, "d":d, "info":info_run}

#Actually perform the UMAP

def perform_umap(umap_params, all_together_vs_marks, no_arc, input_files):
    info_run = umap_params["info"]
    run_name = "UMAP_"+info_run
    #Calculate UMAP on arc tranf data (all_together...)
    umap_emb = pd.DataFrame(umap.UMAP(n_neighbors=umap_params["n"], min_dist=umap_params["m"],
                metric=umap_params["d"], n_components=umap_params["comp"],
                repulsion_strength=umap_params["rs"],
                negative_sample_rate=umap_params["nsr"]).fit_transform(all_together_vs_marks), 
                    columns=[run_name+"_D1",run_name+"_D2"])
    # append umap info columns into untransformed data
    no_arc[run_name+"_D1"] = umap_emb[run_name+"_D1"]
    no_arc[run_name+"_D2"] = umap_emb[run_name+"_D2"]
    
    #Write merged file and individual files with UMAP dimensions
    whole_file = "merged_" + info_run
    no_arc.to_csv(f"./output/2-umap/{whole_file}.txt", index = False, sep = '\t')
    for i in input_files:
        partial_file = i +"__" + info_run
        no_arc.loc[no_arc["file_origin"].str.endswith(input_files[0]),:].to_csv(f"./output/2-umap/{partial_file}.txt", index = False, sep = '\t')

perform_umap(umap_params, all_together_vs_marks, no_arc, input_files)
