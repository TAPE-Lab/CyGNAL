###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~EMD~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# No support for IP/Jupyter notebooks or vs in files (vsNE from Cytobank)

import numpy as np
import pandas as pd
import scprep
import os
import sys
from aux.aux3_emd import *
from aux.aux_functions import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PARAMETER SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
cofactor = 5
normalisation = 'no_norm'
info_run =  input("Write EMD info run (using no spaces!): ")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "3-emd"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 
    
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"

### User Input ###
#Check if user wants to filter the markers based on a .csv marker file
filter_markers = yes_or_NO(
    "Do you want to filter out markers from the panel? (If so please provide .csv file)",
    default="YES")

#Check if user wants to upload the UMAP info to Cytobank
print ("By default concatenated input files will be used as the denominator")
user_defined_denominator = yes_or_NO("User-defined denominator?")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~Preparatory steps and transformation~~~~~~~~~~~~~~~~~~~~#
# set up the files to be analysed (compare_from and compare_to)
# denominator can be concatenated input files or the user-defined txt file

if user_defined_denominator:
    denominator = input("Define denominator (without the '.txt' extension, e.g. sampleA): ")
    compare_to = pd.read_csv(f"{input_dir}/{denominator}.txt", sep = '\t')
    input_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    if len(input_files) ==0:
        sys.exit (f"ERROR: There are no files in {input_dir}!")
else: 
    denominator = 'concatenated-inputs'
    print('Concatenated input files will be used as the denominator')
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
print(f'\nDenominator:\n{denominator}')
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
    compare_from = pd.read_csv(f"{input_dir}/{compare_from_file}", sep = '\t')
    
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
emd_df.to_csv(f"{output_dir}/{whole_file}.txt", index = False,
                    sep = '\t')

