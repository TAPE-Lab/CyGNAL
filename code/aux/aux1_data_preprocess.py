import glob
import os
import re

import numpy as np
import pandas as pd

#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

#Filtering: The function allows you to filter out columns based on a specific pattern, which can be useful for removing columns that are not relevant to your analysis.
def filter_columns(renamed_columns):
    """
    Filters out unnecessary columns from the list of renamed columns.

    Args:
        renamed_columns (list): List of renamed columns.

    Returns:
        tuple: A tuple containing two lists - columns to keep and filtered columns.
    """
    reg_filter = re.compile("^\d+[A-Za-z]+$") #Removes columns with just isotope
    filtered_columns = [] #Stores the columns that where deemed unnecessary
    columns_to_keep = [] #Columns that the reduced file should have
    for i in renamed_columns:
        if reg_filter.search(i):
            filtered_columns.append(i)
        else:
            columns_to_keep.append(i)
    return columns_to_keep, filtered_columns


#Renaming: The function helps standardize and clean the column names, making them more consistent and suitable for further analysis.
def rename_columns(df_file_cols):
    """
    Renames the column names by removing specific patterns and applying renaming rules.

    Args:
        df_file_cols (list): List of column names.

    Returns:
        list: List of renamed column names.
    """
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
#The function generates a panel markers file that can be used to indicate the selection status of markers. The file will contain marker names along with "N" values indicating that none of the markers are selected.
def write_panel_markers(cols, output_dir, info_run):
    """
    Writes the panel markers to a panel markers file.

    Args:
        cols (list): List of markers (column names).
        output_dir (str): Output directory path.
        info_run (str): Information about the run.

    Returns:
        None
    """
    all_markers = cols[0]
    counter_marker = []
    for i in all_markers:
        counter_marker.append("N")
    markers = pd.DataFrame(list(zip(all_markers, counter_marker)))
    markers.to_csv(f"{output_dir}/{info_run}_panel_markers.csv", index=False, header=False)

