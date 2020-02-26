###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~DREMI~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# No support for IP/Jupyter notebooks or vs in files (vsNE from Cytobank)

import pandas as pd
import numpy as np
import scprep
import sys
import os
from itertools import permutations
from aux_functions import yes_or_NO, arcsinh_transf, read_marker_csv
from aux4_dremi import *

import warnings
warnings.filterwarnings('ignore')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DREMI PARAMETERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
cofactor = 5
k = 10
n_bins = 20
n_mesh = 3
return_drevi = False
folder_name = "input/4-dremi"
std_cutoff = [3,4,5]
info_run =  input("Write DREMI info run (using no spaces!): ")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "4-dremi"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"

### User Input ### 
plot = yes_or_NO("Generate plots?")
outliers_removal = yes_or_NO("Perform std-based outlier removal?")
if plot == True:
    if os.path.isdir(f'{output_dir}/plots') == False:
        os.makedirs(f'{output_dir}/plots')

#Check if user wants to filter the markers based on a .csv marker file
filter_markers = yes_or_NO(
    "Do you want to filter out markers from the panel? (If so please provide .csv file)",
    default="YES")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Preparatory steps ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# create the list of txt files to be analysed (all txt files in the input folder)

dremi_files = [file for file in os.listdir(input_dir) if file.endswith(".txt")]
if len(dremi_files) == 0:
    sys.exit("ERROR: no txt files in the input folder")

print('Sample files:')
print('\n'.join([f for f in dremi_files]))

# create a dataframe to store the dremi result
df_info = pd.DataFrame()
dremi_params = {}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform DREMI~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# this block of code compiles the info of the sample, e.g. cell-type, cell-state, condition, etc.
# but the most important information is the filename
# the subset of the data can be done downstream when all the dremi scores have been calculated
for f in dremi_files:
    filename = f.split(".txt")[0]
    data = pd.read_csv(f'{input_dir}/{f}', sep = '\t')
    if filter_markers:
        selected_markers = read_marker_csv(input_dir) #Load .csv with the markers to use in the DREMI calculation -> Often only the PTMs are used
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
            if os.path.isdir(f'{output_dir}/plots/x={marker_x}-y={marker_y}') == False:
                os.makedirs(f'{output_dir}/plots/x={marker_x}-y={marker_y}')
            dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], data_arc[marker_y], 
                                                            k=k, n_bins=n_bins, 
                                                            n_mesh=n_mesh, 
                                                            plot=plot, 
                                                            return_drevi=return_drevi,
                                                            filename=f"{output_dir}/plots/x={marker_x}-y={marker_y}/sample={filename}-x={marker_x}-y={marker_y}.png")
        df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc # save dremi scores without outlier removal regardless of user input

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
                    filename=f"{output_dir}/plots/x={marker_x}-y={marker_y}/sample={filename}-x={marker_x}-y={marker_y}-cutoff={cutoff}.png")
                    df_info_dict[colname_arc] = dremi_wo_outliers_arc
                if num_outliers_total == 0:
                    df_info_dict[colname_arc] = "-" # this is a placeholder
        # Store the info for each marker pair in df_info      
        df_info = df_info.append(df_info_dict, ignore_index=True)    


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Save to file~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# save df_info to file
df_info.to_csv(f"{output_dir}/DREMI_{info_run}.txt", sep = '\t', index=False) 
