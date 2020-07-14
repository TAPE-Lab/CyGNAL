###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~EMD~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#Calculate marker EMD scores per dataset
import re
import os
import sys
import numpy as np
import pandas as pd
import scprep
import fcsparser

from aux.aux3_emd import *
from aux.aux_functions import (read_rFCS, arcsinh_transf, concatenate_fcs, read_marker_csv, yes_or_NO)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PARAMETER SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
cofactor = 5
normalisation = 'no_norm'
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_dir = f"{base_dir}/Analysis/EMD_input"
output_dir = f"{base_dir}/Analysis/EMD_output"

info_run =  input("Write EMD info run (using no spaces!): ")
if len(info_run) == 0:
    print("No info run given. Saving results in UNNAMED")
    info_run = "UNNAMED"
if os.path.isdir(f"{output_dir}/{info_run}") == False:
    os.makedirs(f"{output_dir}/{info_run}")
else:
    if info_run !="UNNAMED":
        sys.exit("ERROR: You already used this name for a previous run. \nUse a different name!")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~User Input~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
filter_markers = yes_or_NO(
    "Do you want to filter out markers from the panel? (If so please provide .csv file)",
    default="YES")

print ("In EMD, the individual Variable distributions are compared against a reference distribution")
print ("By default concatenated input files will be used as the reference distribution.")
user_defined_denominator = yes_or_NO(
                    "Would you like to define your own reference instead?")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~Preparatory steps and transformation~~~~~~~~~~~~~~~~~~~~#
# set up the files to be analysed (compare_from and compare_to)
# denominator can be concatenated input files or the user-defined txt file

if user_defined_denominator:
    txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]
    filelist = txt_filelist+fcs_filelist
    if len(filelist)==0:
        sys.exit (f"ERROR: There are no files in {input_dir}!")
    print(filelist)
    denominator = input("Specify file from the list above to be used as reference (including extension): ")
    denom_path = f"{input_dir}/{denominator}"
    
    if denominator in txt_filelist:
        compare_to = pd.read_csv(denom_path, sep = '\t')
    elif denominator in fcs_filelist:
        try:
            print(denominator)
            compare_to = fcsparser.parse(denom_path, meta_data_only=False)[1]
            reg_pnn = re.compile("(\d+Di$)") #Detect if, despite flag
            pnn_extracted=[]                 #columns match PnN pattern
            for n in compare_to.columns.values.tolist():
                if reg_pnn.search(n):
                    pnn_extracted.append(n)
            if len(pnn_extracted)!=0:
                raise fcsparser.api.ParserFeatureNotImplementedError
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("WARNING: Non-standard .fcs file detected: ", denominator)
            #use rpy2 to read the files and load into python
            compare_to = read_rFCS(denom_path)[0]
    else:
        sys.exit("ERROR: Reference not recognised.\nPlease state exact and full name of file to be used as denominator!")
    input_files = filelist
else: 
    denominator = 'concatenated-inputs'
    print('Concatenated input files will be used as the reference distribution')
    compare_to, input_files = concatenate_fcs(input_dir) #compare_from=inputfile

#Keep only selected markers
if filter_markers:
    selected_markers = read_marker_csv(input_dir)
    print (compare_to.columns)
    file_cols = compare_to.columns
    [x for x in file_cols if x[0].isdigit()]
    for x in file_cols:
        if x[0].isdigit():
            if x not in selected_markers:
                compare_to = compare_to.drop(x, axis=1)
    print (compare_to.columns)

# compare_to = downsample_data(compare_to, info_run, output_dir)
compare_to_arc, marker_list = arcsinh_transf(cofactor, compare_to)

print('Sample files:')
print('\n'.join([f for f in input_files]))
print(f'\nReference:\n{denominator}')
print('\nMarkers:')
print('\n'.join([m for m in marker_list]))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform EMD~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Calculate EMD and save to the output folder (with denominator info run):
# calculate emd and sign the emd score by the difference of median between compare_from and compare_to

emd_df = pd.DataFrame() 
emd_infodict = {}

emd_infodict["denominator"]=denominator
for compare_from_file in input_files:
    emd_infodict["file_origin"] = compare_from_file
    file_path = f"{input_dir}/{compare_from_file}"
    
    if compare_from_file.endswith(".txt"):
        compare_from = pd.read_csv(file_path, sep = '\t')
    else:
        try:
            print(compare_from_file)
            compare_from = fcsparser.parse(file_path, meta_data_only=False)[1]
            reg_pnn = re.compile("(\d+Di$)") #Detect if, despite flag
            pnn_extracted=[]                 #columns match PnN pattern
            for n in compare_from.columns.values.tolist():
                if reg_pnn.search(n):
                    pnn_extracted.append(n)
            if len(pnn_extracted)!=0:
                raise fcsparser.api.ParserFeatureNotImplementedError
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("WARNING: Non-standard .fcs file detected: ", compare_from_file)
            #use rpy2 to read the files and load into python
            compare_from = read_rFCS(file_path)[0]
    
    if filter_markers:
        print (compare_from.columns)
        file_cols = compare_from.columns
        [x for x in file_cols if x[0].isdigit()]
        for x in file_cols:
            if x[0].isdigit():
                if x not in selected_markers:
                    compare_from = compare_from.drop(x, axis=1)
        print (compare_from.columns)

    # print (compare_from)
    # compare_from = downsample_data(compare_from, info_run, output_dir)
    compare_from_arc = arcsinh_transf(cofactor, compare_from)[0]
    #Calculate EMD for each markerVSdenominator
    emd_df = calculate_emd(marker_list, emd_infodict, compare_from_arc,
                            compare_to_arc, normalisation, emd_df)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Save to file~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
whole_file = "EMD_" + info_run
emd_df.to_csv(f"{output_dir}/{info_run}/{whole_file}.txt", index = False,
                    sep = '\t')
