# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'

#%%
import os, glob
import pandas as pd
import numpy as np
import holoviews as hv
import re
from IPython.core.interactiveshell import InteractiveShell

#%%
# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"

#%% [markdown]
#FUTURE WORK: Once I have gone through all steps, implement the code as 
# functions and write and overarching script to run everything as a 
# consolidated pipeline -> Might have to split it whenever Cytobank is involved 


#%%
# prepare file list; put the data files to be processed in the 'input' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME MARKER
filelist = [f for f in os.listdir(f"./input") if f.endswith(".txt")]

#Check the files found in the directory:
print ("Files found in ./input:")
for i in filelist:
    print (i)

#%%
#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

#Renaming
def rename_columns(df_file_cols):
    reg_rename = re.compile("(__[a-z].*$|__\d.*$|_\(.*$|___.*$)")
    df_file_cols_processed = []
    df_file_cols_renamed = []
    for i in df_file_cols:
        try:
            df_file_cols_processed.append(reg_rename.sub("",i))
        except:
            df_file_cols_processed.append(i)
    #Second pass to remove trailing underscores
    for i in df_file_cols_processed:
        try:
            df_file_cols_renamed.append(re.sub(r"_$","",i))
        except:
            df_file_cols_renamed.append(i)
    # Keeping with Xiao's convention, rename Event # to Cell_Index
    for n,i in enumerate(df_file_cols_renamed):
        if i=="Event #":
            df_file_cols_renamed[n] = "Cell_Index"
    
    return df_file_cols_renamed

#Filtering
def filter_columns(renamed_columns):
    reg_filter = re.compile("^\d+[A-Za-z]+$")
    filtered_columns = [] #Stores the columns that where deemed unnecessary
    columns_to_keep = [] #Columns that the reduced file should have
    for i in renamed_columns:
        if reg_filter.search(i):
            filtered_columns.append(i)
        else:
            columns_to_keep.append(i)
    return columns_to_keep, filtered_columns



#%%
# Perform changes and save them to file
cols = []
for i in filelist:
    file = f"./input/{i}"
    df_file = pd.read_csv(file, sep = '\t')
    shape_before = df_file.shape
    df_file_cols = list(df_file.columns)
    
    #%% Perform renaming and filtering
    renamed_columns = rename_columns(df_file_cols)
    columns_to_keep, filtered_columns = filter_columns(renamed_columns)
    df_file.columns = renamed_columns
    f_reduced = df_file[columns_to_keep].iloc[:].copy()
    print ("Removed the following columns: ", filtered_columns)
    
    #Store columns present in each of the input files
    cols.append([x for x in f_reduced.columns if x[0].isdigit()])
    f_reduced.to_csv(f"./output/{i}", index = False, sep = '\t') 
        # index = False to be compatible with Cytobank    
    shape_after = f_reduced.shape
    print(f"file: {i}\n\trows before: {shape_before[0]} - columns before: {shape_before[1]}\n\trows after: {shape_after[0]} - columns after: {shape_after[1]}\n")

#%%
#Add also the generation of a .csv file with the markers in the panel.
#It should be ok to do it here b4 concatenation in the next step because if they are to be concatenaded they shpould already have the same panel of markers

def write_panel_markers(cols):
    all_markers = cols[0]
    counter_marker = []
    for i in all_markers:
        counter_marker.append("N")
    markers = pd.DataFrame(list(zip(all_markers, counter_marker)))
    markers.to_csv(f"./output/panel_markers.csv", index=False, header=False)


if not all(x==cols[0] for x in cols):
    print ("Check your input files: The panels don't match!")
else:
    write_panel_markers(cols)

