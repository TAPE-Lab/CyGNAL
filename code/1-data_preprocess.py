###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Panel editing~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#FIRST STEP: Data and pranel preprocessing. Marker list generation.

import pandas as pd
import OpenSSL.version
import fcswrite
import fcsparser
from aux.aux1_data_preprocess import *
from aux.aux_functions import yes_or_NO
import os
import sys

sequential_mode = vars(sys.modules[__name__])['__package__']
print(sequential_mode) #Will populate if run from superior script

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
input_dir = f"../Raw_Data"
output_dir = f"../Preprocessed_Data"

# prepare file list; put the data files to be processed in the 'input' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME MARKER
txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]
filelist = txt_filelist+fcs_filelist

if len(txt_filelist) == 0 and len(fcs_filelist)==0:
    sys.exit(f"ERROR: There are no files in {input_dir}!")

info_run =  input("Write info run (using no spaces!): ")
if len(info_run) == 0:
    print("No info run given. Saving results in UNNAMED")
    info_run = "UNNAMED"

if os.path.isdir(f"{output_dir}/{info_run}") == False:
    os.makedirs(f"{output_dir}/{info_run}")
else:
    if info_run !="UNNAMED":
        sys.exit("ERROR: You already used this name for a previous run. \nUse a different name!")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

# def preprocess_files (filelist, format_filelist, input_dir, output_dir):
cols = []
for i in filelist:
    file_path = f"{input_dir}/{i}"
    if i in txt_filelist:
    # if format_filelist=="txt":
        df_file = pd.read_csv(file_path, sep = '\t')
        print(i)
    else: 
        try: #Use fcsparser to read the fcs data files
            print (i)
            metafcs,df_file = fcsparser.parse(file_path, meta_data_only=False)
            nonstandard_FCS = "NO"
            #print ("remove:\n", metafcs)
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("Non-standard .fcs file detected: ", i)
            print("Metadata will be droppped and file will be saved as .txt by default")
            from aux.aux_functions import read_rFCS #Import only if needed
            #use rpy2 to read the files and load into python
            df_file = read_rFCS(file_path)
            #print ("remove:\n", df_file)
            nonstandard_FCS ="YES" #Offer to save as .txt by default
    
    shape_before = df_file.shape
    df_file_cols = list(df_file.columns)
    
    #%% Perform renaming and filtering
    try:
        renamed_columns = rename_columns(df_file_cols)
        columns_to_keep, filtered_columns = filter_columns(renamed_columns)
        df_file.columns = renamed_columns
        f_reduced = df_file[columns_to_keep].iloc[:].copy()
        print ("Removed the following columns: ", filtered_columns)
        
        #Store columns present in each of the input files
        cols.append([x for x in f_reduced.columns if x[0].isdigit()])
        
        shape_after = f_reduced.shape
        print (
            f"file: {i}\n\trows before: {shape_before[0]} - columns before: {shape_before[1]}\n\trows after: {shape_after[0]} - columns after: {shape_after[1]}\n")
    except:
        print("Column names processing and filtering failed. Check the format!",
                "Using original unchanged panel")
        f_reduced = df_file

    #Saving files:
    if i in txt_filelist:
        answ = yes_or_NO("File is a .txt. Would you like to also save it as an .fcs?")
        f_reduced.to_csv(f"{output_dir}/{info_run}/{i}", index = False, sep = '\t') 
        # index = False to be compatible with Cytobank
        if answ:
            #SAVE AS FCS
            print(list(f_reduced.columns))
            print(f_reduced.to_numpy())
            fcswrite.write_fcs(f"{output_dir}/{info_run}/{i}.fcs", 
                                chn_names=list(f_reduced.columns),
                                compat_chn_names=False, 
                                data=f_reduced.to_numpy())
            
    else:
        answ = yes_or_NO("File is an .fcs. Would you like to also save it as a .txt?", 
                    default=nonstandard_FCS)
        #SAVE AS FCS
        fcswrite.write_fcs(f"{output_dir}/{info_run}/{i}", 
                            chn_names=list(f_reduced.columns),
                            compat_chn_names=False, 
                            data=f_reduced.to_numpy())
        print(answ==True)
        if answ:
            print("Converting .fcs to .txt")
            f_reduced.to_csv(f"{output_dir}/{info_run}/{i}.txt", index = True, sep = '\t') 

#Add also the generation of a .csv file with the markers in the panel.
if not all(x==cols[0] for x in cols):
    sys.exit("ERROR when generating shared marker panel:\nCheck your input files as THE PANELS DON'T MATCH!") 
else:
    write_panel_markers(cols, f"{output_dir}/{info_run}", info_run)


#RELIC CODE#
#Saving fcs should be done at the end ina  simialr check as the one above for .txt and fcs.
        #   If fcs, ask user which format to save results as: .txt, .fcs, both

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
