###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~UMAP~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# No support for IP/Jupyter notebooks or vs in files (vsNE from Cytobank)

import pandas as pd
import numpy as np
import umap
import sys
import os
from aux2_umap_functions import *
from aux_functions import concatenate_fcs, arcsinh_transf

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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#include here the information that would be helpful to understand the umaps
info_run =  input("Write UMAP info run (using no spaces!): ")


# Perform umap analysis, but let's first create and concatenate any 
# files that we will be suing as input
# Input: Output from step 1, originally cytobank non-transformed .txt exports

folder_name = "input/2-umap"    # set up input directory


#~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform concatenation~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

no_arc, input_files = concatenate_fcs(folder_name)


#~~~~~~~~~~~~~~~~~~~~Downsampling if using multiple files~~~~~~~~~~~~~~~~~~~~~#
#Test lenght of input files -> Go with minimun denominator -> select, at random,
# that number of cells from other files

#Using sample()
if no_arc["file_origin"].value_counts().size > 1:
    print ("Downsampling taking place. Check output folder for more info")
    print (no_arc["file_origin"].value_counts())
    no_arc = downsample_data(no_arc, info_run)
    print (no_arc["file_origin"].value_counts())
else:
    print ("Only one input file detected; no downsampling")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform transformation~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Literature recommends cofactor of 5 for cytof data
cofactor = 5

arc, cols = arcsinh_transf(cofactor, no_arc)
#Storing marker columns for later use below


# ### Step 2: Make umaps
#~~~~~~~~~~~~~~~Define the markers used for UMAP calculation~~~~~~~~~~~~~~~~~~#
#Read them from a .csv file in ./input
#Sanity check
marker_files = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".csv")]
if len(marker_files) != 1:
    sys.exit("ERROR: There should be ONE .csv file with the markers to use in the input folder!")

marker_file = pd.read_csv(f"{folder_name}/{marker_files[0]}", header=None)

#Group columns of the dataframe based on the type of measurement
not_markers_cols = [column for column in arc.columns if column not in cols]
all_markers_cols = cols.copy()

# define the v's for umap calculation (vs_markers_cols)
not_these = [] # columns to be excluded for umap calculation
vs_markers_cols = identify_markers(marker_file)
no_vs_markers_cols = [column for column in all_markers_cols if 
                        column not in vs_markers_cols]

# keep the columns ('v's) needed for umap calculation (all_together_vs_marks)
all_together_vs_marks = arc.loc[:, vs_markers_cols].copy()

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

#Actually perform the UMAP
perform_umap(umap_params, all_together_vs_marks, arc, input_files)
print (arc)