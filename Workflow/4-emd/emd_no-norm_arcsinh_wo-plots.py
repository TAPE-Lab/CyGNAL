# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Workflow/4-emd'))
	print(os.getcwd())
except:
	pass

#%%
import numpy as np
import pandas as pd
import scprep
import os

#%%
import holoviews as hv
from IPython.core.interactiveshell import InteractiveShell
hv.extension("bokeh", width=90) # wide cells
InteractiveShell.ast_node_interactivity = "all" # display all output in each cell

#%%
# parameter setup
cofactor = 5
k = 10
n_bins = 20
n_mesh = 3
plot = True
return_drevi = False

normalisation = 'no-norm'

#%% Function to concatenate all files
def concatenate_fcs(folder_name):
    filenames_no_arcsinh = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]
    no_arc = pd.DataFrame()
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for file in filenames_no_arcsinh:
        fcounter += 1
        df = pd.read_csv(f"{folder_name}/{file}", sep = '\t')
        df["file_origin"] = str(fcounter)+" | "+ file # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        no_arc = no_arc.append(df, ignore_index=True)
    return no_arc, filenames_no_arcsinh

#%%
# set up the files to be analysed (compare_from and compare_to)
# change the name of the 'compare_to‘ fcs file if needed

compare_to, filelist = concatenate_fcs('input')
markers_compare_to = [m for m in list(compare_to.columns) if m[0].isdigit()]
compare_to_arc = compare_to.loc[:,markers_compare_to].apply(lambda x: np.arcsinh(x/cofactor)) # arcsinh transformation

compare_from = [file for file in filelist if file.endswith(".txt")]
denominator = 'concatenated-input' # change this as needed (a user prompt?)

print('Sample files:')
print('\n'.join([f for f in compare_from]))
print(f'\nDenominator:\n{denominator}')
print('\nMarkers:')
print('\n'.join([m for m in markers_compare_to]))

#%% Function to calculate EMD
# calculate emd and sign the emd score by the difference of median between compare_from and compare_to
def emd_arc(data_from_arc, data_to_arc, marker, normalisation):
    
    df_info_dict[f"median_{normalisation}_arc_compare_from"] = data_from_arc[marker].median()
    df_info_dict[f"median_{normalisation}_arc_compare_to"] = data_to_arc[marker].median()
    df_info_dict[f"median_diff_{normalisation}_arc_compare_from_vs_to"] = data_from_arc[marker].median() - data_to_arc[marker].median()
    
    if (data_from_arc[marker].median() - data_to_arc[marker].median()) >= 0:
        emd_arc = scprep.stats.EMD(data_from_arc[m], data_to_arc[m])
    if (data_from_arc[marker].median() - data_to_arc[marker].median()) < 0:
        emd_arc = -scprep.stats.EMD(data_from_arc[m], data_to_arc[m])

    return emd_arc

#%% Calculate EMD and save to the output folder (with denominator info)
df_info = pd.DataFrame()
df_info_dict = {}
df_info_dict["compare_to"] = denominator

for compare_from_file in compare_from:
    df_info_dict["compare_from"] = f"{compare_from_file}".split('.txt')[0]

    compare_from = pd.read_csv(f'./input/{compare_from_file}', sep = '\t')
    markers_compare_from = [m for m in list(compare_from.columns) if m[0].isdigit()]
    compare_from_arc = compare_from.loc[:, markers_compare_from].apply(lambda x: np.arcsinh(x/cofactor))
    
    for m in markers_compare_from:
        if m in markers_compare_to:
            df_info_dict["marker"] = m
            df_info_dict[f"EMD_{normalisation}_arc"] = emd_arc(compare_from_arc, compare_to_arc, m, normalisation) 
            # save the info in the dict (df_info_dict) to the dataframe df_info
            df_info = df_info.append(df_info_dict, ignore_index = True)   
        else:
            print("THE COMPARE_FROM AND COMPARE_TO PANELS DON'T MATCH")

# save info in the dataframe df_info to a txt file
df_info.to_csv(f"./output/emd_denominator={denominator}.txt", sep="\t")