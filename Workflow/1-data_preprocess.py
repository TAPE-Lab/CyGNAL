###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Panel editing~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#FIRST STEP: Data and pranel preprocessing. Marker list generation.
#Jupyter/IP no longer supported here

import pandas as pd
import OpenSSL.version
from aux1_data_preprocess import *
import os
import sys

#FUTURE WORK: Once I have gone through all steps, implement the code as 
# functions and write and overarching script to run everything as a 
# consolidated pipeline -> Might have to split it whenever Cytobank is involved 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "1-data_preprocess"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 
    
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# prepare file list; put the data files to be processed in the 'input' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME MARKER
filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]

#Check the files found in the directory:
print ("Input files:")
for i in filelist:
    print (i)

#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

cols = []
for i in filelist:
    file = f"{input_dir}/{i}"
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
    f_reduced.to_csv(f"{output_dir}/{i}", index = False, sep = '\t') 
        # index = False to be compatible with Cytobank    
    shape_after = f_reduced.shape
    print (
        f"file: {i}\n\trows before: {shape_before[0]} - columns before: {shape_before[1]}\n\trows after: {shape_after[0]} - columns after: {shape_after[1]}\n")


#Add also the generation of a .csv file with the markers in the panel.
if not all(x==cols[0] for x in cols):
    print ("Check your input files: The panels don't match!")
else:
    write_panel_markers(cols, output_dir)