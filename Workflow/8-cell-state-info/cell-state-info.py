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

#%% [markdown]
### Usage
#### Note: This script is used when Cyclin B1 is gated on the *histogram*.
# This script takes txt files exported from Cytobank as input
# The gating strategy is decribed in the Organoid Methods Paper, Supplementary Figure 2
# When Cyclin B1 is gated on the histogram, G1 cells can be identified as a population and exported as a standalone txt file
# That makes the assignment of the G1 cell-state easier than the one implemented with the use of cell-index
# However, I prefer to gate Cyclin B1 on biaxial plots... (XQ) So this script should probably not be used.
# The output dataframes have two extra columns: 'cell-state' and 'cell-state_num'
# 0 - apoptosis, 1 - G0, 2 - G1, 3 - S-phase, 4 - G2, 5 - M-phase

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
# generate a list of cell-types
cell_type = [f.split('_')[0] for f in filelist]
cell_type = list(set(cell_type))
cell_type

cell_state = [f.split('.txt')[0].split('_')[-1] for f in filelist]
cell_state = list(set(cell_state))
cell_state

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

#%%
dfs_sub = {}
for c_type in cell_type:
    sub = 'dfs_' + c_type
    dfs_sub[sub] = {k:v for k, v in dfs.items() if k.split('_')[0] == c_type}

dfs_sub.keys()

#%%
for k, v in dfs_sub.items(): 
    c_type = k.split('_')[1]
    data = pd.DataFrame()

    for k1, v1 in v.items():
        data = pd.concat([data, v1])
    
    data.to_csv(f"./output/{c_type}_w-cell-state.csv", index = False)


#%%
