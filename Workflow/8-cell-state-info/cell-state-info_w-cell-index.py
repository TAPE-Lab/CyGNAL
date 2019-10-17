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
 
dfs = {}
for file in filelist:
    df = pd.read_csv(f'./input/{file}', sep = '\t', index_col = 0)
    c_type = file.split('_')[0]
    c_state = file.split('.txt')[0].split('_')[-1]
    dfs[c_type + '_' + c_state] = df

dfs.keys()

#%%
# subset the dfs dictionary based on cell-types

dfs_sub = {}
for c_type in cell_type:
    sub = 'dfs_' + c_type
    dfs_sub[sub] = {k:v for k, v in dfs.items() if k.split('_')[0] == c_type}

dfs_sub.keys()

dfs_sub_copy = dfs_sub.copy()

#%%
for k, v in dfs_sub.items(): 
    for k1, v1 in v.items():
        v[k1] = v1.iloc[:,0].copy()

#%%
for k, v in dfs_sub.items(): 
    c_type = k.split('_')[1]
    ungated = c_type + '_Ungated'
    # data = pd.DataFrame()

    for k1, v1 in v.items():
        c_state = k1.split('_')[1]
        df_ungated = v[ungated]

        if c_state != 'Ungated':
            v[ungated] = pd.concat([df_ungated, v1]).drop_duplicates(keep = False)
    # data.to_csv(f"./output/{c_type}_w-cell-state.csv", index = False)

#%%
for k, v in dfs_sub_copy.items(): 
    c_type = k.split('_')[1]
    g1 = c_type + '_G1'
    index = list(dfs_sub['dfs_' + c_type][c_type + '_Ungated'])

    for k1, v1 in v.items():
        c_state = k1.split('_')[1]
        if c_state == 'Ungated':
            v1 = v1.loc[v1['Cell_Index'].isin(index)].copy()

#%%
for k, v in dfs_sub.items(): 
    c_type = k.split('_')[1]
    data = pd.DataFrame()

    for k1, v1 in v.items():
        data = pd.concat([data, v1])
    
    data.to_csv(f"./output/{c_type}_w-cell-state.csv", index = False)

#%%
dfs = {}
for file in filelist:
    df = pd.read_csv(f'./input/{file}', sep = '\t', index_col = 0)
    # df.reset_index(drop = True, inplace = True)
    c_type = file.split('_')[0]
    c_state = file.split('.txt')[0].split('_')[-1]
    df['cell-state'] = c_state
    if c_state == 'apoptosis':
        df['cell-state_num'] = 0
    if c_state == 'G0':
        df['cell-state_num'] = 1
    if c_state == 'G1':
        df['cell-state_num'] = 2    
    if c_state == 'S-phase':
        df['cell-state_num'] = 3
    if c_state == 'G2':
        df['cell-state_num'] = 4
    if c_state == 'M-phase':
        df['cell-state_num'] = 5 

    dfs[c_type + '_' + c_state] = df

dfs.keys()