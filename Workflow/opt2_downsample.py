import pandas as pd
import numpy as np
import umap
import sys
import os
from aux_functions import concatenate_fcs, downsample_data

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "opt2_downsample"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 
    
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

info_run =  input("Write downsampling info run (using no spaces!): ")

concatenated_df, imput_files = concatenate_fcs(input_dir)

downsampled_conc_df = downsample_data(concatenated_df, info_run, output_dir)

#Divide concatenated into separate files
state_group = downsampled_conc_df.groupby("cell-state")
print (downsampled_conc_df.groupby("cell-state").size())

for name, group in state_group:
    print(name)
    print(group)
    group.to_csv(f"{output_dir}/{name}_downsample_{info_run}.txt",
                    index = False, sep = '\t')
