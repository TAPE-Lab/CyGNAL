
import os  # Fix importing from diff. directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import numpy as np
import pandas as pd
import umap
from aux.aux_functions import concatenate_fcs, downsample_data

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
folder_name = "opt2_downsample"

input_dir = f"{base_dir}/Utils_Data/input/{folder_name}"
output_dir = f"{base_dir}/Utils_Data/output/{folder_name}"

filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
if len(filelist) == 0:
    sys.exit(f"ERROR: There are no .txt files in {input_dir}!")
#Check the files found in the directory:
print ("Downsample script supports only .txt files. Input files:")
for i in filelist:
    print (i)
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
    group.to_csv(f"{output_dir}/{info_run}/{name}_downsample_{info_run}.txt", index = False, sep = '\t')

print(f"Downsampled files saved in {output_dir}")


#Cell state sepration -> Interactive queastion, defaul file origin
# #Divide concatenated into separate files
# state_group = downsampled_conc_df.groupby("cell-state")
# print (downsampled_conc_df.groupby("cell-state").size())

# for name, group in state_group:
#     print(name)
#     print(group)
#     group.to_csv(f"{output_dir}/{name}_downsample_{info_run}.txt",
#                     index = False, sep = '\t')
