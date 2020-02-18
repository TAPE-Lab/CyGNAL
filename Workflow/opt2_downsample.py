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

print ("This script now downsamples multiple files on the input to the condition with less cells")
info_run =  input("Write downsampling info run (using no spaces!): ")

concatenated_df = concatenate_fcs(input_dir)[0]
downsampled_conc_df = downsample_data(concatenated_df, info_run, output_dir)

# Since after downsampling file_origin is also an index, drop index from dataframe
for name, group in downsampled_conc_df.reset_index(drop=True).groupby("file_identifier"):
    print (name)
    print (group)
    group.reset_index()
    # group['post-downsample_cell-index'] = group.index
    group.to_csv(f"{output_dir}/{info_run}/{name}_downsample_{info_run}.txt", index = True, sep = '\t')

#Cell state sepration -> Interactive queastion, defaul file origin
# #Divide concatenated into separate files
# state_group = downsampled_conc_df.groupby("cell-state")
# print (downsampled_conc_df.groupby("cell-state").size())

# for name, group in state_group:
#     print(name)
#     print(group)
#     group.to_csv(f"{output_dir}/{name}_downsample_{info_run}.txt",
#                     index = False, sep = '\t')



