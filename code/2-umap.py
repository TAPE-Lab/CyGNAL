###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~UMAP~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#Perfom UMAP on pre-processed datasets
import os
import re
import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import umap

from aux.aux2_umap import *
from aux.aux_functions import (arcsinh_transf, concatenate_fcs,
                            downsample_data, read_marker_csv, yes_or_NO)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PARAMETER SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
nn = "no-norm"
rs = 2.0
nsr = 8
n = 15
m = 0.1
comp = 2
d = "euclidean"
low_memory = False #Add support for low_memory flag to umap run

cofactor = 5
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Future WIP: Add support for sequential hands off -> if flag use set of seq i/o
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_dir = f"{base_dir}/Analysis/UMAP_input"
output_dir = f"{base_dir}/Analysis/UMAP_output"

info_run =  input("Write UMAP info run (using no spaces!): ")
if len(info_run) == 0:
    print("No info run given. Saving results in UNNAMED")
    info_run = "UNNAMED"

if os.path.isdir(f"{output_dir}/{info_run}") == False:
    os.makedirs(f"{output_dir}/{info_run}")
else:
    if info_run !="UNNAMED":
        sys.exit("ERROR: You already used this name for a previous run. \nUse a different name!")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~Preliminary steps and transformation~~~~~~~~~~~~~~~~~~~~~~#
#Concatenate# -> Read input .txt and .fcs. Sanity check. Concatenate
no_arc, input_files = concatenate_fcs(input_dir) #Does sanity check of files in input

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
df_vs_markers_cols.to_csv(f"{output_dir}/{info_run}/markers_for_{info_run}.csv") # save markers used for UMAP in output folder
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


#~~~~~~~~~~~~~~~~~~~~~~~~~~Perform  and save UMAP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Define UMAP parameters

umap_params = {"nn":nn, "rs":rs, "nsr":nsr, "n":n, "m":m, "comp":comp, "d":d,
                "info":info_run}
#Run UMAP
no_arc = perform_umap(umap_params, all_together_vs_marks, no_arc)

#Save UMAP results:
if len(set(no_arc["file_origin"])) > 1: # more than one file
    whole_file = "merged_" + "UMAP_"+info_run
    no_arc.to_csv(f"{output_dir}/{info_run}/{whole_file}.txt", 
                    index = False, sep = '\t')

for i in input_files: #Split merged file by file_origin->
    file_origin = i.split('.')[0] #>- allows to import conditions to cytobank
    partial_file = file_origin + "_" + "UMAP_"+info_run
    no_arc.loc[no_arc["file_identifier"] == file_origin,:].to_csv(
        f"{output_dir}/{info_run}/{partial_file}.txt", index = False,
        sep = '\t')

