###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~UMAP~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# No support for IP/Jupyter notebooks or vs in files (vsNE from Cytobank)

import pandas as pd
import numpy as np
import umap
import sys
import os
from aux2_umap import *
from aux_functions import concatenate_fcs, arcsinh_transf, read_marker_csv, downsample_data

import warnings
warnings.filterwarnings('ignore')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~UMAP PARAMETERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
nn = "no-norm"
rs = 2.0
nsr = 8
n = 15
m = 0.1
comp = 2
d = "euclidean"
info_run =  input("Write UMAP info run (using no spaces!): ")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#include here the information that would be helpful to understand the umaps


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "2-umap"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./output/{folder_name}/{info_run}") == False:
    os.makedirs(f"./output/{folder_name}/{info_run}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 

input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Input: Output from step 1, originally cytobank non-transformed .txt exports


#~~~~~~~~~~~~~~~~~~~Preliminary steps and transformation~~~~~~~~~~~~~~~~~~~~~~#
#Concatenate#
no_arc, input_files = concatenate_fcs(input_dir)
# input_files = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]
# no_arc = concatenate_fcs(folder_name)

#Downsampling#
#Test lenght of input files -> Go with minimun denominator -> select, at random,
# that number of cells from other files
if no_arc["file_origin"].value_counts().size > 1:
    downs_inputs = yes_or_NO(
        "Multiple input files detected. Would you like to donwsample the number of cells?",
        default="YES")
    if downs_inputs:
        print ("Downsampling taking place. Check output folder for more info")
        print (no_arc["file_origin"].value_counts())
        no_arc = downsample_data(no_arc, info_run, output_dir)
        print (no_arc["file_origin"].value_counts())
    else:
        print ("Multiple input files; no downsampling")
else:
    print ("Only one input file detected; no downsampling")

#Transformation#
#Literature recommends cofactor of 5 for cytof data
cofactor = 5
arc, cols = arcsinh_transf(cofactor, no_arc)
#Storing marker columns for later use below


#~~~~~~~~~~~~~~~Define the markers used for UMAP calculation~~~~~~~~~~~~~~~~~~#

#Group columns of the dataframe based on the type of measurement
not_markers_cols = [column for column in arc.columns if column not in cols]
all_markers_cols = cols.copy()

# define the v's for umap calculation (vs_markers_cols)
not_these = [] # columns to be excluded for umap calculation
vs_markers_cols = read_marker_csv(input_dir) #Read them from a .csv file in ./input
print (vs_markers_cols)
df_vs_markers_cols = pd.DataFrame(vs_markers_cols, columns=['marker'])
df_vs_markers_cols.index = np.arange(1, len(df_vs_markers_cols)+1)
df_vs_markers_cols.to_csv(f"./output/{folder_name}/{info_run}/markers_for_{info_run}.csv") # save markers used for UMAP in output folder
no_vs_markers_cols = [column for column in all_markers_cols if 
                        column not in vs_markers_cols]

print (arc.columns)
# keep the columns ('v's) needed for umap calculation (all_together_vs_marks)
all_together_vs_marks = arc.loc[:, vs_markers_cols].copy()
print (all_together_vs_marks)

print(f"Markers used for UMAP calculation: \n")
print('\n'.join([m for m in all_together_vs_marks]))
print(f"\n Number of markers used: {len(all_together_vs_marks.columns)}")


#~~~~~~~~~~~~~~~~~~~Optional: z-score transformation~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Z-SCORE: Not used now, interactive inplementation on later stages of the pipeline
# z-score transformation (for the Organoid Methods Paper, only applied to supplementary figure 1)
# all_together_vs_marks.head()
# all_together_vs_marks = all_together_vs_marks.apply(zscore)
# all_together_vs_marks.head()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform UMAP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Define UMAP parameters

umap_params = {"nn":nn, "rs":rs, "nsr":nsr, "n":n, "m":m, "comp":comp, "d":d,
                "info":info_run}

#Actually perform the UMAP with arc tranf data and save to original untransformed matrix
perform_umap(umap_params, all_together_vs_marks, no_arc, input_files, output_dir, info_run)
