###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Panel editing~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#FIRST STEP: Data and pranel preprocessing. Marker list generation.

import pandas as pd
import OpenSSL.version
import fcswrite
import fcsparser
from aux1_data_preprocess import *
import os
import sys


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
txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]

if len(txt_filelist) == 0 and len(fcs_filelist)==0:
    sys.exit(f"ERROR: There are no files in {input_dir}!")
else:
    #Check the files found in the directory:
    print ("Input files:")
    if len(txt_filelist) == 0:
        for i in fcs_filelist:
            print (i)
        format_filelist = "fcs"
        filelist = fcs_filelist
    elif len(fcs_filelist) == 0:
        for i in txt_filelist:
            print (i)
        format_filelist = "txt"
        filelist = txt_filelist
    else:
        sys.exit(f"ERROR: Please have EITHER .txt files OR .fcs files, but not both!")

#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

info_run =  input("Write info run (using no spaces!): ")

# def preprocess_files (filelist, format_filelist, input_dir, output_dir):
cols = []
for i in filelist:
    file = f"{input_dir}/{i}"
    if format_filelist=="txt":
        df_file = pd.read_csv(file, sep = '\t')
        print(df_file)
    else: #Use fcsparser to read the fcs data files (no meta support)
        print("test fcs: detected, should be reading them now")
        print(file)
        try:
            df_file = fcsparser.parse(file, meta_data_only=False)[1]
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("Yep, Cytobank's fcs are utter and complete shit")
            print("So I guess I'll have to try and hijack an R package for this")
            #Since Flowcytometry ALSO uses fcsparser under the hood...
            #So options are: -Use R to load .fcs if formatted shity (thanks cytobank..)
            #                  -Write our own fcs parser (lol, that's certainly too much effort)
            #                  -Complain to Cytobank or try and get fcsparser fixed to support cytobank's shity fcss..)
        print (df_file)
sys.exit("Bye!")
#     shape_before = df_file.shape
#     df_file_cols = list(df_file.columns)
    
#     #%% Perform renaming and filtering
#     renamed_columns = rename_columns(df_file_cols)
#     columns_to_keep, filtered_columns = filter_columns(renamed_columns)
#     df_file.columns = renamed_columns
#     f_reduced = df_file[columns_to_keep].iloc[:].copy()
#     print ("Removed the following columns: ", filtered_columns)
    
#     #Store columns present in each of the input files
#     cols.append([x for x in f_reduced.columns if x[0].isdigit()])
#     f_reduced.to_csv(f"{output_dir}/{i}", index = False, sep = '\t') 
#         # index = False to be compatible with Cytobank    
#     shape_after = f_reduced.shape
#     print (
#         f"file: {i}\n\trows before: {shape_before[0]} - columns before: {shape_before[1]}\n\trows after: {shape_after[0]} - columns after: {shape_after[1]}\n")
# #Add also the generation of a .csv file with the markers in the panel.
# if not all(x==cols[0] for x in cols):
#     sys.exit("ERROR: Check your input files; THE PANELS DON'T MATCH!") 
# else:
#     write_panel_markers(cols, output_dir, info_run)


