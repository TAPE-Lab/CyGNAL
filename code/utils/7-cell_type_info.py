#! python3
###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Cell-Type-info~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################

#### Note: This script is used to integrate cell-type info into ungated populations.
# This script takes txt files exported from Cytobank as input
# The gating strategy is decribed in the Organoid Methods Paper, Supplementary Figure 2
# The assignment of cell types is based on the 'Cell_Index' column
# Since there will be cells positive for more than one cell-type markers, the cell-type identification 
# works by assigning 0/1's to all the six cell-type markers used in the panel

# setup the environment
import sys
import os
import copy
import pandas as pd
import numpy as np
from code.aux.aux_functions import yes_or_NO

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Sanity Check~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
file_name_format = yes_or_NO("Are all the files named in the 'sample-name_cell-type' format?")
if file_name_format == False:
    sys.exit(f"Please rename the files to the 'sample_cell-type' format\n Accepted cell-types (literal): stem, paneth, enteroendocrine, tuft, goblet, and enterocyte") 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "7-cell_type_info"
if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    # sys.exit("ERROR: There is no input folder") 

c_type_list = ['stem', 'paneth', 'enteroendocrine', 'tuft', 'goblet', 'enterocyte']

# prepare files
filelist = [f for f in os.listdir(f"./input/{folder_name}") if f.endswith(".txt")]

# generate lists of sample-id and cell-types for iteration
# the sample files should be named in the following format:
# 'sample-id_cell-type.txt'

# generate lists of cell-indices for each file
for file in filelist:
    sample = file.split('_')[0]
    cell_type = file.split('_')[1].split('.')[0]
    df = pd.read_csv(f'./input/{folder_name}/{file}', sep = '\t')
    df_cell_index = df[['Cell_Index']]
    df_cell_index.columns = ['Cell_Index']
    df_cell_index.to_csv(f'./input/{folder_name}/{sample}_{cell_type}_cell-index.txt', sep = '\t', index = False)

# prepare files again, this time cell-indices only
filelist = [f for f in os.listdir(f"./input/{folder_name}") if f.endswith("cell-index.txt")]

sample_id = [f.split('_')[0] for f in filelist]
sample_id= list(set(sample_id))
print("Sample(s):")
print('\n'.join([s for s in sample_id]))

cell_type = [f.split('_')[1] for f in filelist]
cell_type = list(set(cell_type))
print("\nCell-types:")
print([t for t in cell_type])

# generate a dictionary of dataframes
# keys: sample-id_cell-type_cell-state
# values: a dataframe per txt file 
dfs = {}
for file in filelist:
    df = pd.read_csv(f'./input/{folder_name}/{file}', sep = '\t')
    s_id = file.split('_')[0]
    c_type = file.split('_')[1]
    # c_state = file.split('.txt')[0].split('_')[-1]
    # dfs[s_id + '_' + c_type + '_' + c_state] = df
    dfs[s_id + '_' + c_type] = df

# dfs.keys()

# subset the dfs dictionary based on sample-id and cell-type
# initialise a nested dictionary: dfs_sub[sample-id][cell-type]
dfs_sub = {}
for s_id in sample_id:
    dfs_sub[s_id] = {}
    for c_type in cell_type:
        dfs_sub[s_id][c_type] = dfs[s_id + '_' + c_type]

# for s_id in sample_id:
#     print(f'{s_id}: {dfs_sub[s_id].keys()}')

# make a copy of the dfs_sub dictionary for cell-state annotation later
dfs_sub_copy = copy.deepcopy(dfs_sub)

for s_id in sample_id:    
    df_ungated = dfs_sub_copy[s_id]['Ungated'].copy()
    num_of_cell = len(df_ungated.index)

    for c_type in c_type_list:
        print(f'Now processing {c_type} in the sample {s_id}...')

        df_index_list = list(dfs_sub_copy[s_id][c_type].loc[:,'Cell_Index'])
        df_cell_type_init = pd.DataFrame(0, index=np.arange(num_of_cell), columns=[c_type])
        df_cell_type_init = df_ungated.join(df_cell_type_init)
        df_cell_type_init.loc[df_cell_type_init['Cell_Index'].isin(df_index_list), c_type] = 1 # This is fast!
        df_ungated = df_ungated.join(df_cell_type_init[c_type])
    
    df_ungated.to_csv(f"./output/{folder_name}/{s_id}_cell-type-info.txt", index = False, sep = '\t')

print(f"Output file(s) saved in the folder './output/{folder_name}'")