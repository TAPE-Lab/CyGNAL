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
filelist = txt_filelist+fcs_filelist

if len(txt_filelist) == 0 and len(fcs_filelist)==0:
    sys.exit(f"ERROR: There are no files in {input_dir}!")


#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

info_run =  input("Write info run (using no spaces!): ")

# def preprocess_files (filelist, format_filelist, input_dir, output_dir):
cols = []
for i in filelist:
    file = f"{input_dir}/{i}"
    if i in txt_filelist:
    # if format_filelist=="txt":
        df_file = pd.read_csv(file, sep = '\t')
        print(i,df_file)
    else: #Use fcsparser to read the fcs data files (no meta support)
        print("test fcs: detected, should be reading them now")
        print(i)
        try:
            df_file = fcsparser.parse(file, meta_data_only=False)[1]
            print ("FCSPARSER TO THE RESCUE!:", i, df_file)
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("Yep, Cytobank's fcs are utter and complete shit:", i)
            #read.FCS from flocore IS WORKING!!!!!!

                                                                               #Since Flowcytometry ALSO uses fcsparser under the hood...
                                                                                #So options are: -Use R to load .fcs if formatted shity (thanks cytobank..)
                                                                                #                  -Write our own fcs parser (lol, that's certainly too much effort)
                                                                                #                  -Complain to Cytobank or try and get fcsparser fixed to support cytobank's shity fcss..)
                                                                               
                                                                               #FLOWKIT AND FLOIO generate proper fcs files but the intensities in them aren't the right numbers
                                                                                # df_file = flowkit.Sample(file)
                                                                                # print(df_file)
                                                                                # print(df_file.channels)
                                                                                # if os.path.isdir(f"{input_dir}/Reformatted_FCSs") == False:
                                                                                #     os.makedirs(f"{input_dir}/Reformatted_FCSs")
                                                                                # print(df_file.export("test.fcs", source="raw"))

                                                                                # df_file_channels = []
                                                                                # df_file=flowio.FlowData(file)
                                                                                # print("File", df_file)
                                                                                # print("Evenets",df_file.events)
                                                                                # # print("Text is useless", df_file.text)
                                                                                # print("Channels", df_file.channels)
                                                                                # for key in sorted(df_file.channels.keys()):
                                                                                #     print(df_file.channels[key])
                                                                                #     try:
                                                                                #         df_file_channels.append(df_file.channels[key]["PnN"])
                                                                                #     except:
                                                                                #         print ("PnN short names weren't found. Trying instead with PnS names")
                                                                                #         df_file_channels.append(df_file_channels[key]["PnS"])
                                                                                # print (df_file_channels)
            
        
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


