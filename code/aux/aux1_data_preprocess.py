import glob
import os
import re

import numpy as np
import pandas as pd

#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

#Filtering
def filter_columns(renamed_columns):
    reg_filter = re.compile("^\d+[A-Za-z]+$") #Removes columns with just isotope
    filtered_columns = [] #Stores the columns that where deemed unnecessary
    columns_to_keep = [] #Columns that the reduced file should have
    for i in renamed_columns:
        if reg_filter.search(i):
            filtered_columns.append(i)
        else:
            columns_to_keep.append(i)
    return columns_to_keep, filtered_columns


#Renaming
def rename_columns(df_file_cols):
    reg_rename = re.compile("(__[a-z].*$|__\d.*$|_\(.*$|___.*$)")
        #First two options match ending constructs with double underscores
        #Third option matches endings within brackets
    df_file_cols_processed = []
    df_file_cols_renamed = []
    df_file_cols_final = []

    for i in df_file_cols: #First pass to remove most issues
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
    #Third pass replace '__' with '_'
    for i in df_file_cols_renamed:
        try:
            df_file_cols_final.append(re.sub(r"__","_",i))
        except:
            df_file_cols_final.append(i)
    # Keeping with Xiao's convention, rename Event # to Cell_Index
    for n,i in enumerate(df_file_cols_final):
        if i=="Event #":
            df_file_cols_final[n] = "Cell_Index"
    
    return df_file_cols_final


#Add also the generation of a .csv file with the markers in the panel.
#It should be ok to do it here b4 concatenation in the next step because if 
# they are to be concatenaded they shpould already have the same panel of markers
def write_panel_markers(cols, output_dir, info_run):
    all_markers = cols[0]
    counter_marker = []
    for i in all_markers:
        counter_marker.append("N")
    markers = pd.DataFrame(list(zip(all_markers, counter_marker)))
    markers.to_csv(f"{output_dir}/{info_run}_panel_markers.csv", index=False, header=False)

