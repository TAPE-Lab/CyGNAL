###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Cell-State-info~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################

#### Note: This script is used when Cyclin B1 is gated on the *biaxial plot*.
# This script takes txt files exported from Cytobank as input
# The gating strategy is decribed in the Organoid Methods Paper, Supplementary Figure 2
# Since G1 cells are identified with negative selection, they are not in an explicit cell gate
# Therefore the identification of G1 cells is based on the 'Cell_Index' column (ungated minus all the others)
# The output dataframes have two extra columns: 'cell-state' and 'cell-state_num'
# 0 - apoptosis, 1 - G0, 2 - G1, 3 - S-phase, 4 - G2, 5 - M-phase
# For each cell-type, 6 input files are needed: Ungated, apoptosis, G0, S-phase, G2, and M-phase
# The files need to be named as 'sample-name_cell-type_cell-state'

# setup the environment
import sys
import os
import copy
import pandas as pd
import numpy as np
from code.aux.aux_functions import yes_or_NO

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Sanity Check~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
file_name_format = yes_or_NO("Are all the files named in the 'sample-name_cell-type_..._cell-state' format?")
if file_name_format == False:
    sys.exit(f"Please rename the files to the 'sample_cell-type_cell-state' format\n Accepted cell-states (literal): Ungated, apoptosis, G0, S-phase, G2, and M-phase") 


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Preparatory steps~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "6-cell_state_info"

# prepare files
filelist = [f for f in os.listdir(f"./input/{folder_name}") if f.endswith(".txt")]

# generate lists of sample-id, cell-types, and cell-states for iteration
# the sample files should be named in the following format:
# 'sample-id_cell-type_..._cell-state.txt'

sample_id = [f.split('_')[0] for f in filelist]
sample_id= list(set(sample_id))
print("Samples:")
print('\n'.join([s for s in sample_id]))

cell_type = [f.split('_')[1] for f in filelist]
cell_type = list(set(cell_type))
print("\nCell-types:")
print([t for t in cell_type])

print("\nCell-states:")
cell_state = [f.split('.txt')[0].split('_')[-1] for f in filelist]
cell_state = list(set(cell_state))
print([s for s in cell_state])

# generate a dictionary of dataframes
# keys: sample-id_cell-type_cell-state
# values: a dataframe per txt file 
dfs = {}
for file in filelist:
    df = pd.read_csv(f'./input/{folder_name}/{file}', sep = '\t', index_col = 0)
    s_id = file.split('_')[0]
    c_type = file.split('_')[1]
    c_state = file.split('.txt')[0].split('_')[-1]
    dfs[s_id + '_' + c_type + '_' + c_state] = df

# dfs.keys()

# subset the dfs dictionary based on sample-id and cell-type
# initialise a nested dictionary: dfs_sub[sample-id][cell-type]
dfs_sub = {}
for s_id in sample_id:
    dfs_sub[s_id] = {}
    for c_type in cell_type:
        dfs_sub[s_id][c_type] = {k:v for k,v in dfs.items() if k.split('_')[0] 
            == s_id and k.split('_')[1] == c_type}

# for s_id in sample_id:
#     print(f'{s_id}: {dfs_sub[s_id].keys()}')

# make a copy of the dfs_sub dictionary for cell-state annotation later
dfs_sub_copy = copy.deepcopy(dfs_sub)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Cell state ID~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# keep only the 'Cell_Index' column to compare each cell-state population against the 'Ungated'
# this overwrites the dfs_sub dictionary and replaces the dataframes with Series...
# may not be the best solution
for k, v in dfs_sub.items(): 
    for k1, v1 in v.items():
        for k2, v2 in v1.items():
            v1[k2] = v2.loc[:,'Cell_Index'].copy()

# for each sample, perform the following steps:
# for each cell-type, concatenate all the gated cell-states (apoptosis, G0, S, 
# G2, and M) with the 'Ungated' population and then remove duplicates so all 
# the gated cell-states will be removed from the ungated population 
#  --> leaving the indices of cells in G1
# now the values of the dfs_sub dictionary are the indices of cells of all the six cell-states
for k, v in dfs_sub.items(): 
    for k1, v1 in v.items():
        s_id = k
        c_type = k1
        g1 = s_id + '_' + c_type + '_G1'
        df_tmp = pd.DataFrame()

        for k2, v2 in v1.items():
            df_tmp = pd.concat([df_tmp, v2])

        df_tmp = df_tmp.drop_duplicates(keep = False).copy()
        v1[g1] = df_tmp.iloc[:, 0] # save the indices of G1 cells as a pandas Series

# use the indices of G1 cells stored in dfs_sub to subset the dfs_sub_copy and 
# get the G1 population of each cell-type
for s_id in sample_id:
    for c_type in cell_type:
        df_ungated = dfs_sub_copy[s_id][c_type][s_id + '_' + c_type + '_Ungated'].copy()
        g1 = s_id + '_' + c_type + '_G1'
        g1_idx = list(dfs_sub[s_id][c_type][g1])
        dfs_sub_copy[s_id][c_type][g1] = df_ungated.loc[
                                            df_ungated['Cell_Index'].isin(g1_idx)].copy()

# add the cell-state information (text & numerical) to the dataframes
for k, v in dfs_sub_copy.items(): 
    s_id = k
    for k1, v1 in v.items():
        c_type = k1
        for k2, v2 in v1.items():
            c_state = k2.split('_')[-1]
            v2['cell-state'] = c_state

            if c_state == 'apoptosis':
                v2['cell-state_num'] = 0
            if c_state == 'G0':
                v2['cell-state_num'] = 1
            if c_state == 'G1':
                v2['cell-state_num'] = 2    
            if c_state == 'S-phase':
                v2['cell-state_num'] = 3
            if c_state == 'G2':
                v2['cell-state_num'] = 4
            if c_state == 'M-phase':
                v2['cell-state_num'] = 5


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Save to file~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# concatenate all the cell-state dataframes within each cell-type and save as txt files
for k, v in dfs_sub_copy.items(): 
    s_id = k
    for k1, v1 in v.items():
        c_type = k1
        data = pd.DataFrame()

        for k2, v1 in v1.items():
            c_state = k2.split('_')[-1]
            if c_state != 'Ungated':
                data = pd.concat([data, v1])
        
        data.sort_values(by='Cell_Index').to_csv(f"./output/{folder_name}/{s_id}_{c_type}_w-cell-state.txt", index = False, sep = '\t')

print(f"Output files saved in the folder './output/{folder_name}'")
