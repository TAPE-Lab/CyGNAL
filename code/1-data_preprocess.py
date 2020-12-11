###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Pre-processing~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#FIRST STEP: Data and pranel preprocessing. Marker list generation.
import os
import re
import sys

import fcsparser
import fcswrite
import pandas as pd

from aux.aux1_data_preprocess import *
from aux.aux_functions import yes_or_NO

#Future WIP: Add support for sequential hands off -> if flag use set of seq i/o
# sequential_mode = vars(sys.modules[__name__])['__package__']
# print(sequential_mode) #Will populate if run from superior script

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_dir = f"{base_dir}/Raw_Data"
output_dir = f"{base_dir}/Preprocessed_Data"

# prepare file list; put the data files to be processed in the 'input' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME panel
txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]
filelist = txt_filelist+fcs_filelist

if len(filelist)==0:
    sys.exit (f"ERROR: There are no files in {input_dir}!")
if len(txt_filelist)!=0:
    print("Found the following .txt files: ", txt_filelist)
    txt_sopts = yes_or_NO("Would you like to save the processed .txt files also in .fcs format?")
if len(fcs_filelist)!=0:
    print("Found the following .fcs files: ", fcs_filelist)
    fcs_sopts = yes_or_NO("Would you like to save the processed .fcs files also in .txt format?")


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


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Pre-processing~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
cols = []
no_filter=False

for i in filelist:
    file_path = f"{input_dir}/{i}"
    if i in txt_filelist:
    # if format_filelist=="txt":
        df_file = pd.read_csv(file_path, sep = '\t')
        print(i)
    else: 
        try: #Use fcsparser to read the fcs data files
            print (i)
            metafcs,df_file = fcsparser.parse(file_path, meta_data_only=False,
                                                channel_naming='$PnS')
            # nonstandard_FCS = "NO"
            reg_pnn = re.compile("(\d+Di$)") #Detect if, despite flag
            pnn_extracted=[]                 #columns match PnN pattern
            for n in df_file.columns.values.tolist():
                if reg_pnn.search(n):
                    pnn_extracted.append(n)
            if len(pnn_extracted)!=0:
                raise fcsparser.api.ParserFeatureNotImplementedError
            # print(df_file.columns)
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("WARNING: Non-standard .fcs file detected: ", i)
            print("This might take a while. Please take care and check the output")
            from aux.aux_functions import read_rFCS  # Import only if needed

            #use rpy2 to read the files and load into python
            df_file, no_filter = read_rFCS(file_path)
            # print(df_file.columns)
            #print ("remove:\n", df_file)
            # nonstandard_FCS ="YES" #Offer to save as .txt by default
    
    shape_before = df_file.shape
    df_file_cols = list(df_file.columns)
      
    #%% Perform renaming and filtering
    try:
        if no_filter==False:
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
        else:
            print("No filtering being performed")
            f_reduced = df_file
            cols.append(df_file_cols)
    except:
        print("Column names processing and filtering failed. Check the format!",
                "Using original unchanged panel")
        f_reduced = df_file
        cols.append(df_file_cols)
    
    #Add Cell_Index column
    if "Cell_Index" not in f_reduced.columns:
        print("MISSING CELL_INDEX")
        f_reduced.reset_index(inplace=True)
        f_reduced.rename({"index": "Cell_Index"}, axis="columns", inplace=True)
    f_reduced["Cell_Index"] = pd.to_numeric(f_reduced["Cell_Index"])
    print(f_reduced) #Print final dataframe

    #Saving files#:
    if i in txt_filelist:
        f_reduced.to_csv(f"{output_dir}/{info_run}/Pro_{i}", index = False, sep = '\t') 
        # index = False to be compatible with Cytobank
        if txt_sopts:
            #SAVE AS FCS
            fcswrite.write_fcs(f"{output_dir}/{info_run}/Pro_{i}.fcs", 
                                chn_names=list(f_reduced.columns),
                                compat_chn_names=False, 
                                data=f_reduced.to_numpy())
            
    else:
        # answ = yes_or_NO("File is an .fcs. Would you like to also save it as a .txt?", 
        #             default=nonstandard_FCS)
        fcswrite.write_fcs(f"{output_dir}/{info_run}/Pro_{i}", 
                            chn_names=list(f_reduced.columns),
                            compat_chn_names=False, 
                            data=f_reduced.to_numpy())
        if fcs_sopts:
            print("Converting .fcs to .txt")
            f_reduced.to_csv(f"{output_dir}/{info_run}/Pro_{i}.txt", index = False, sep = '\t') #Changed to index=False


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Panel markers~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
if not all(x==cols[0] for x in cols):
    sys.exit("ERROR when generating shared marker panel:\nCheck your input files as THE PANELS DON'T MATCH!") 
else:
    write_panel_markers(cols, f"{output_dir}/{info_run}", info_run)

