#FIRST STEP: Data and pranel preprocessing. Marker list generation.
#Jupyter/IP no longer supported here

import pandas as pd
from panel_editing_functions import *

#FUTURE WORK: Once I have gone through all steps, implement the code as 
# functions and write and overarching script to run everything as a 
# consolidated pipeline -> Might have to split it whenever Cytobank is involved 


# prepare file list; put the data files to be processed in the 'input' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME MARKER
filelist = [f for f in os.listdir(f"./input") if f.endswith(".txt")]

#Check the files found in the directory:
print ("Files found in ./input:")
for i in filelist:
    print (i)

#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

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
    # name = file.split(".")[0]
    # print (i)
    # print (file)
    # print(name)
    f_reduced.to_csv(f"./output/{i}", index = False, sep = '\t') 
        # index = False to be compatible with Cytobank    
    shape_after = f_reduced.shape
    print (f"file: {i}\n\trows before: {shape_before[0]} - columns before: {shape_before[1]}\n\trows after: {shape_after[0]} - columns after: {shape_after[1]}\n")


#Add also the generation of a .csv file with the markers in the panel.
if not all(x==cols[0] for x in cols):
    print ("Check your input files: The panels don't match!")
else:
    write_panel_markers(cols)

