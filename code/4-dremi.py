###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~DREMI~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#Calculate marker DREMI scores per pair of markers in each dataset
import os
import re
import sys
import warnings
warnings.filterwarnings('ignore')
from itertools import permutations

import fcsparser
import numpy as np
import pandas as pd
import scprep

from aux.aux4_dremi import *
from aux.aux_functions import (arcsinh_transf, read_marker_csv, read_rFCS,
                                yes_or_NO)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PARAMETER SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
cofactor = 5
k = 10
n_bins = 20
n_mesh = 3
return_drevi = False
folder_name = "input/4-dremi"
std_cutoff = [3,4,5]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_dir = f"{base_dir}/Analysis/DREMI_input"
output_dir = f"{base_dir}/Analysis/DREMI_output"

info_run =  input("Write DREMI info run (using no spaces!): ")
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

print("Outliers can be detected using ST Deviation cutoffs.\nBy default this will not be performed.")
outliers_removal = yes_or_NO("Perform std-based outlier removal?")

print("For each combination of 2 markers, intensity, density and probability plots can be generated.")
plot = yes_or_NO("By default no plots will be generated.\nGenerate plots?")
if plot == True:
    os.makedirs(f'{output_dir}/{info_run}/plots')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Preparatory steps ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# create the list of txt files to be analysed (all txt files in the input folder)
txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]
dremi_files = txt_filelist+fcs_filelist
if len(dremi_files)==0:
    sys.exit (f"ERROR: There are no files in {input_dir}!")

print("Sample files:")
print("\n".join([f for f in dremi_files]))
print("Calculating...")

# create a dataframe to store the dremi result
df_info = pd.DataFrame()
dremi_params = {}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform DREMI~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# this block of code compiles the info of the sample, e.g. cell-type, cell-state, condition, etc.
# but the most important information is the filename
# the subset of the data can be done downstream when all the dremi scores have been calculated
for f in dremi_files:
    file_path = f"{input_dir}/{f}"
    filename = f.split(".")[0]
    if f in txt_filelist:
        print ("Working on ",f)
        data = pd.read_csv(file_path, sep = '\t')
    else:
        try: #Use fcsparser to read the fcs data files
            print(f)
            data = fcsparser.parse(file_path, meta_data_only=False)[1]
            reg_pnn = re.compile("(\d+Di$)") #Detect if, despite flag
            pnn_extracted=[]                 #columns match PnN pattern
            for n in data.columns.values.tolist():
                if reg_pnn.search(n):
                    pnn_extracted.append(n)
            if len(pnn_extracted)!=0:
                raise fcsparser.api.ParserFeatureNotImplementedError
        except fcsparser.api.ParserFeatureNotImplementedError:
                print("WARNING: Non-standard .fcs file detected: ", f)
                #use rpy2 to read the files and load into python
                data = read_rFCS(file_path)[0]
    if filter_markers: #Load .csv with the markers to use -> Often PTMs
        selected_markers = read_marker_csv(input_dir) 
        data = data.loc[:, selected_markers] # Remove unwanted markers
    data_arc, markers = arcsinh_transf(cofactor, data)

    # generate the list of marker-marker pairs for dremi calculation 
    marker_pairs = [comb for comb in list(permutations(markers, 2))]
    for marker_x, marker_y in marker_pairs:
        df_info_dict = {}   
        df_info_dict["file_origin"] = filename
        df_info_dict["marker_x"] = marker_x
        df_info_dict["marker_y"] = marker_y
        df_info_dict["marker_x_marker_y"] = marker_x + '_' + marker_y
        df_info_dict["num_of_cells"] = data.shape[0]

        if plot == True:
            if os.path.isdir(f'{output_dir}/{info_run}/plots/x={marker_x}-y={marker_y}') == False:
                os.makedirs(f'{output_dir}/{info_run}/plots/x={marker_x}-y={marker_y}')
                
        dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], 
                                    data_arc[marker_y], k=k, n_bins=n_bins, 
                                    n_mesh=n_mesh, plot=plot, 
                                    return_drevi=return_drevi,
                                    filename=f"{output_dir}/{info_run}/plots/x={marker_x}-y={marker_y}/sample={filename}-x={marker_x}-y={marker_y}.png")
        df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc 
            # save dremi scores without outlier removal regardless of user input

        if outliers_removal == True: #EXPERIMENTAL, not fully tested
            for cutoff in std_cutoff:
                colname_arc = f"wo_outliers_arcsinh_cutoff={cutoff}_std_DREMI_score"
                #Using outlier_removal auxiliary function
                (num_outliers_total, df_wo_outliers) = outlier_removal(
                                                        data_arc, cutoff, 
                                                        marker_x, marker_y, 
                                                        df_info_dict)
                if num_outliers_total > 0:
                    dremi_wo_outliers_arc = scprep.stats.knnDREMI(
                                            df_wo_outliers[marker_x],
                                            df_wo_outliers[marker_y], k=k,
                                            n_bins=n_bins, n_mesh=n_mesh,
                                            plot=plot, return_drevi=return_drevi,
                                            filename=f"{output_dir}/{info_run}/plots/x={marker_x}-y={marker_y}/sample={filename}-x={marker_x}-y={marker_y}-cutoff={cutoff}.png")
                    df_info_dict[colname_arc] = dremi_wo_outliers_arc
                if num_outliers_total == 0:
                    df_info_dict[colname_arc] = "-" # this is a placeholder
        # Store the info for each marker pair in df_info      
        df_info = pd.concat([df_info, df_info_dict], ignore_index=True)    


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Save to file~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# save df_info to file
df_info.to_csv(f"{output_dir}/{info_run}/DREMI_{info_run}.txt", sep = '\t', index=False) 
