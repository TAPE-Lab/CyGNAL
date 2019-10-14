# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'step-n_cell-state-info'))
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
import rpy2.robjects as ro
from rpy2.robjects.packages import importr 
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

pandas2ri.activate()
%load_ext rpy2.ipython

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
