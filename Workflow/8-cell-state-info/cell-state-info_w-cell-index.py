# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Workflow/8-cell-state-info'))
	print(os.getcwd())
except:
	pass

#%%
# setup the environment
import os, glob
import pandas as pd
import numpy as np
import holoviews as hv
import copy
from IPython.core.interactiveshell import InteractiveShell

#%%
# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"

#%%
# prepare files
filelist = [f for f in os.listdir(f"./input") if f.endswith(".txt")]
filelist

#%%
# generate lists of cell-types and cell-states for iteration
 
cell_type = [f.split('_')[0] for f in filelist]
cell_type = list(set(cell_type))
cell_type

cell_state = [f.split('.txt')[0].split('_')[-1] for f in filelist]
cell_state = list(set(cell_state))
cell_state

#%%
# generate a dictionary of dataframes
# keys: cell-type_cell-state
# values: a dataframe per txt file 
 
dfs = {}
for file in filelist:
    df = pd.read_csv(f'./input/{file}', sep = '\t', index_col = 0)
    c_type = file.split('_')[0]
    c_state = file.split('.txt')[0].split('_')[-1]
    dfs[c_type + '_' + c_state] = df

dfs.keys()

#%%
# subset the dfs dictionary based on cell-types
# keys: cell_type
# values: a group of dataframes per cell-type

dfs_sub = {}
for c_type in cell_type:
    dfs_sub[c_type] = {k:v for k, v in dfs.items() if k.split('_')[0] == c_type}
dfs_sub.keys()

# make a copy of the dfs_sub dictionary for cell-state annotation later
dfs_sub_copy = copy.deepcopy(dfs_sub)

#%%
# keep only the 'Cell_Index' column to compare each cell-state population against the 'Ungated'
# this overwrites the dfs_sub dictionary and replaces the dataframes with Series...
# may not be the best solution

for k, v in dfs_sub.items(): 
    for k1, v1 in v.items():
        v[k1] = v1.loc[:,'Cell_Index'].copy()

#%%
# for each cell-type, perform the following steps:
# concatenate all the gated cell-states (apoptosis, G0, S, G2, and M) with the 'Ungated' population and then remove duplicates
# so all the gated cell-states will be removed from the ungated population -- leaving the indices of cells in G1
# now the values of the dfs_sub dictionary are the indices of cells of all the six cell-states

for k, v in dfs_sub.items(): 
    c_type = k.split('_')[1]
    g1 = c_type + '_G1'
    df_tmp = pd.DataFrame()

    for k1, v1 in v.items():
        df_tmp = pd.concat([df_tmp, v1])

    df_tmp = df_tmp.drop_duplicates(keep = False).copy()
    v[g1] = df_tmp.iloc[:, 0] # save the indices of G1 cells as a pandas Series

#%%
# use the indices of G1 cells stored in dfs_sub to subset the dfs_sub_copy and get the G1 population of each cell-type

for c_type in cell_type:
    df_ungated = dfs_sub_copy[c_type][c_type + '_Ungated'].copy()
    g1 = c_type + '_G1'
    g1_idx = list(dfs_sub[c_type][g1])
    dfs_sub_copy[c_type][g1] = df_ungated.loc[df_ungated['Cell_Index'].isin(g1_idx)].copy()

#%%
# add the cell-state information (text & numerical) to the dataframes
for k, v in dfs_sub_copy.items(): 
    c_type = k.split('_')[1]

    for k1, v1 in v.items():
        c_state = k1.split('_')[1]
        v1['cell-state'] = c_state

        if c_state == 'apoptosis':
            v1['cell-state_num'] = 0
        if c_state == 'G0':
            v1['cell-state_num'] = 1
        if c_state == 'G1':
            v1['cell-state_num'] = 2    
        if c_state == 'S-phase':
            v1['cell-state_num'] = 3
        if c_state == 'G2':
            v1['cell-state_num'] = 4
        if c_state == 'M-phase':
            v1['cell-state_num'] = 5

#%%
# concatenate all the cell-state dataframes within each cell-type and save as txt files
for k, v in dfs_sub_copy.items(): 
    c_type = k.split('_')[1]
    data = pd.DataFrame()

    for k1, v1 in v.items():
        c_state = k1.split('_')[1]
        if c_state != 'Ungated':
            data = pd.concat([data, v1])
    
    data.to_csv(f"./output/{c_type}_w-cell-state.txt", index = False, sep = '/t')