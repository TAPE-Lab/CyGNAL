###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~DREMI~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# No support for IP/Jupyter notebooks or vs in files (vsNE from Cytobank)

import pandas as pd
import numpy as np
import scprep
import sys
from itertools import permutations
from aux_functions import yes_or_NO


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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

### User Input ### 
plot = yes_or_NO("Generate plots?")
outliers_removal = yes_or_NO("Perform std-based outlier removal?")


# create new folders to save the output of the script: plots and info
if plot == True:
    if os.path.isdir('./output/plots') == False:
        os.makedirs('./output/plots')

if os.path.isdir('./output/info') == False:
    os.makedirs('./output/info')


# create the list of txt files to be analysed (all txt files in the input folder)

dremi_files = [file for file in os.listdir('./input') if file.endswith(".txt")]
if len(dremi_files) == 0:
    sys.exit("Error: no txt files in the input folder")

print('Sample files:')
print('\n'.join([f for f in dremi_files]))


# find outliers for both marker_x and marker_y based on cufoffs of standard deviations
# return the number of outliers and a dataframe after outlier removal
# update the df_info_dict with the number of outliers

def outlier_removal(df, cutoff, marker_x, marker_y):
    num_outliers_total = 0
    num_outliers_x = 0
    num_outliers_y = 0
    
    df_outliers_x = df[(np.abs(df[marker_x]-df[marker_x].mean()) > (cutoff*df[marker_x].std()))]
    df_outliers_y = df[(np.abs(df[marker_y]-df[marker_y].mean()) > (cutoff*df[marker_y].std()))]
    num_outliers_x += df_outliers_x.shape[0]
    num_outliers_y += df_outliers_y.shape[0]
    
    df_wo_outliers = df[(np.abs(df[marker_x]-df[marker_x].mean()) <= (cutoff*df[marker_x].std())) & (np.abs(df[marker_y]-df[marker_y].mean()) <= (cutoff*df[marker_y].std()))]
    df_only_outliers_xy = df[(np.abs(df[marker_x]-df[marker_x].mean()) > (cutoff*df[marker_x].std())) | (np.abs(df[marker_y]-df[marker_y].mean()) > (cutoff*df[marker_y].std()))]
    num_outliers_total += df_only_outliers_xy.shape[0]

    # Update the df_info_dict dictionary with outlier info
    df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_x"] = num_outliers_x
    df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_y"] = num_outliers_y
    df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_total"] = num_outliers_total

    return(num_outliers_total, df_wo_outliers)


# create a dataframe to store the dremi result
df_info = pd.DataFrame()

# this block of code compiles the info of the sample, e.g. cell-type, cell-state, condition, etc.
# but the most important information is the filename
# the subset of the data can be done downstream when all the dremi scores have been calculated
for f in dremi_files:
    filename = f.split(".txt")[0]

    data = pd.read_csv(f'./input/{f}', sep = '\t') # may or may not have an index column
    markers = [m for m in list(data.columns) if m[0].isdigit()]
    data_arc = data.loc[:, markers].apply(lambda x: np.arcsinh(x/cofactor))
    
    # generate the list of marker-marker pairs for dremi calculation 
    marker_pairs = [comb for comb in list(permutations(markers, 2))]
    
    for marker_x, marker_y in marker_pairs:

        # compile the sample info 
        df_info_dict = {}   
        df_info_dict["file"] = filename
        df_info_dict["marker_x"] = marker_x
        df_info_dict["marker_y"] = marker_y
        df_info_dict["marker_x-marker_y"] = marker_x + '_' + marker_y
        df_info_dict["num_of_cells"] = data.shape[0]
        
        if plot == True:
            os.makedirs(f'./output/plots/x={marker_x}_y={marker_y}')

        # save dremi scores without outlier removal
        # this step is always run regardless of the True or False value of the User Input plot / outliers_removal
        dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], data_arc[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, 
                                                        filename=f"./output/plots/x={marker_x}_y={marker_y}/sample={filename}_x={marker_x}_y={marker_y}.png")
        df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc

        if outliers_removal == True:
            for cutoff in std_cutoff:
                colname_arc = f"wo_outliers_arcsinh_cutoff={cutoff}_std_DREMI_score"

                (num_outliers_total, df_wo_outliers) = outlier_removal(data_arc, cutoff, marker_x, marker_y)
                if num_outliers_total > 0:
                    dremi_wo_outliers_arc = scprep.stats.knnDREMI(df_wo_outliers[marker_x], df_wo_outliers[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"./output/plots/x={marker_x}_y={marker_y}/sample={filename}_x={marker_x}_y={marker_y}_cutoff={cutoff}.png")
                    df_info_dict[colname_arc] = dremi_wo_outliers_arc
                if num_outliers_total == 0:
                    df_info_dict[colname_arc] = "-" # this is a placeholder
                    
        df_info = df_info.append(df_info_dict, ignore_index=True) # save the info in the dict (df_info_dict) to a dataframe (df_info)   

# save info in the dataframe df_info to a txt file
df_info.to_csv('./output/info/dremi_info.txt', sep = '\t', index=False) 
