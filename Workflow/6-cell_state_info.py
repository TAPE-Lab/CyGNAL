###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Cell-State-info~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################

# setup the environment
import sys
import os
import copy
import pandas as pd
import numpy as np
from aux_functions import yes_or_NO

#### Note: This script is used when Cyclin B1 is gated on the *histogram*.
# This script takes txt files exported from Cytobank as input
# The gating strategy is described in the Organoid Methods Paper, Supplementary Figure 2
# When Cyclin B1 is gated on the histogram, G1 cells can be identified as a population and exported as a standalone txt file
# That makes the assignment of the G1 cell-state easier than the one implemented with the use of cell-index
# The output dataframes have two extra columns: 'cell-state' and 'cell-state_num'
# 0 - apoptosis, 1 - G0, 2 - G1, 3 - S-phase, 4 - G2, 5 - M-phase

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Sanity Check~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
file_name_format = yes_or_NO("Are all the files named in the 'sample-name_cell-type_..._cell-state' format?")
if file_name_format == False:
    sys.exit(f"Please rename the files to the 'sample_cell-type_cell-state' format\n Accepted cell-states (literal): Apoptosis, G0, S-phase, G2, and M-phase") 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Preparatory steps~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "6-cell_state_info"

# prepare files
filelist = [f for f in os.listdir(f"./input/{folder_name}") if f.endswith(".txt")]

# generate sample summary: cell-type per sample
# the sample files should be named in the following format:
# 'sample-id_cell-type_..._cell-state.txt'

sample_id = list(set([f.split('_')[0] for f in filelist]))
for s in sample_id:
    sample_files = [f for f in os.listdir(f"./input/{folder_name}") if f.startswith(f'{s}')]
    cell_type = list(set([f.split('_')[1] for f in sample_files]))
    print(f"Sample: {s}\nCell-type(s):{cell_type}\n")

# for each sample, generate a dictionary 'dfs' with cell-types as keys (dictionary level 1)
# then for each cell-type, generate a nested dictionary with cell-states as keys
# the value of the dfs[sample_id][cell_type][cell_state] item is a dataframe for each cell-state
# with the newly assigned 'cell-state' and 'cell-state_num' columns 
dfs = {}
for s_id in sample_id:
    dfs[s_id] = {}
    sample_filelist = [f for f in os.listdir(f"./input/{folder_name}") if f.startswith(f'{s_id}')]
    for s_file in sample_filelist:
        c_type = s_file.split('.txt')[0].split('_')[1]
        dfs[s_id][c_type] = {}
        c_type_filelist = [f for f in os.listdir(f"./input/{folder_name}") if f.startswith(f'{s_id}_{c_type}')]
        for file in c_type_filelist:
            df = pd.read_csv(f'./input/{folder_name}/{file}', sep = '\t', index_col = 0)
            c_state = file.split('.txt')[0].split('_')[-1]
            df['cell-state'] = c_state
            if c_state.lower() == 'apoptosis':
                df['cell-state_num'] = 0
            elif c_state.lower() == 'g0':
                df['cell-state_num'] = 1
            elif c_state.lower() == 'g1':
                df['cell-state_num'] = 2
            elif c_state.lower() == 's-phase':
                df['cell-state_num'] = 3
            elif c_state.lower() == 'g2':
                df['cell-state_num'] = 4
            elif c_state.lower() == 'm-phase':
                df['cell-state_num'] = 5 
            else:
                df['cell-state_num'] = -1 # for mislabelled cell-states
            dfs[s_id][c_type][c_state]= df

# iterate through the nested dictionaries, concatenate all cell-state dataframes per sample/cell-type
for k, v in dfs.items():
    s_id = k
    for k1, v1 in v.items():
        c_type = k1
        data = pd.DataFrame()
        for k2, v2 in v1.items():
            data = pd.concat([data, v2])
        data.to_csv(f"./output/{folder_name}/{s_id}_{c_type}_w-cell-state.txt", sep = '\t', index = False)