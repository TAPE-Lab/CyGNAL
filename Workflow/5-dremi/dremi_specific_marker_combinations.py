# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'Workflow/5-dremi'))
	print(os.getcwd())
except:
	pass

#%%

import pandas as pd
import numpy as np
import scprep
import sys
from itertools import permutations

import warnings
warnings.filterwarnings('ignore')

#%%
# wide cells
import holoviews as hv
from IPython.core.interactiveshell import InteractiveShell
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"

#%%
# parameter setup
cofactor = 5
k = 10
n_bins = 20
n_mesh = 3
plot = False
return_drevi = False

# optional: removal of outliers based on standard deviation 
outliers_removal = False
num_std_for_outliers = [3,4,5]

#%%
# create new folders to save the output of the script: plots, plots/drevi plots, and info
if plot == True:
    if os.path.isdir('./output/DREVI_plots') == False:
        os.makedirs('./output/DREVI_plots')

if os.path.isdir('./output/info') == False:
    os.makedirs('./output/info')

#%%
# create the list of fcs files to be analysed (all fcs files in the dremi_dir folder)

dremi_files = [file for file in os.listdir('./input') if file.endswith(".txt")]
if len(dremi_files) == 0:
    sys.exit("Error: no txt files in the input folder")

print('Sample files:')
print('\n'.join([f for f in dremi_files]))

#%%
# find outliers for both marker_x and marker_y; create a dataframe with outliers removed

def z_score_outliers_removal(df, cutoff, marker_x, marker_y):
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

    return(df_outliers_x, df_outliers_y, df_only_outliers_xy, df_wo_outliers, num_outliers_x, num_outliers_y, num_outliers_total)

#%%
# create a dataframe to store the dremi result
df_info = pd.DataFrame()

#################################################################################################
# this block of code compiles the info of the sample, e.g. cell-type, cell-state, condition, etc.
# but the most important information is the filename
# the subset of the data can be done downstream when all the dremi scores have been calculated
for f in dremi_files:
    filename = f.split(".fcs")[0]
#################################################################################################

    data = pd.read_csv(f'./input/{f}', sep = '\t')
    markers = [m for m in list(data.columns) if m[0].isdigit()]
    data_arc = data.loc[:, markers].apply(lambda x: np.arcsinh(x/cofactor))
    
    # generate the list of marker-marker pairs for dremi calculation 
    marker_pairs = [comb for comb in list(permutations(list(markers["marker"]), 2))]
    
    # create folders to store drevi plots, arcsinh and no-arcsinh
    # for dremi calculation, the raw data needs to be arcsinh-transformed 
    
    for marker_x, marker_y in marker_pairs:
        
        #marker_comb_drevi_plots_dir = os.path.join(file_drevi_plots_dir, f"x={marker_x}_y={marker_y}")
        #os.makedirs(marker_comb_drevi_plots_dir)
        
        #arc_marker_comb_drevi_plots_dir = os.path.join(marker_comb_drevi_plots_dir, "arcsinh")
        #os.makedirs(arc_marker_comb_drevi_plots_dir)
        
        #no_arc_marker_comb_drevi_plots_dir = os.path.join(marker_comb_drevi_plots_dir, "no-arcsinh")
        #os.makedirs(no_arc_marker_comb_drevi_plots_dir)
        
        # compile the sample info 
        
        df_info_dict = {}   
        df_info_dict["file"] = f
        df_info_dict["marker_x"] = marker_x
        df_info_dict["marker_y"] = marker_y
        df_info_dict["num_of_cells"] = data.shape[0]
#         df_info_dict["cell_state"] = cell_state
#         df_info_dict["cell_type"] = cell_type
#         df_info_dict["day"] = day
        df_info_dict["fcs_filename"] = f
        
        # dremi calculation and drevi plot generation

        if outliers_removal == False:
            
            #####
            # save plots and dremi scores; with outliers
#             dremi_with_outliers_no_arc = scprep.stats.knnDREMI(data[marker_x], data[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"{no_arc_marker_comb_drevi_plots_dir}/from_{cell_type}_{cell_state}_cells_x={marker_x}_y={marker_y}_no-arc.png")
#             dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], data_arc[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"{arc_marker_comb_drevi_plots_dir}/from_{cell_type}_{cell_state}_cells_x={marker_x}_y={marker_y}_arc.png")
            
#             df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc
#             df_info_dict["with_outliers_no-arcsinh_DREMI_score"] = dremi_with_outliers_no_arc
            ##### 
            
#             ######
#             # save dremi scores if we don't want the plots; with outliers
            dremi_with_outliers_no_arc = scprep.stats.knnDREMI(data[marker_x], data[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi)
            dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], data_arc[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi)
            
            df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc
            df_info_dict["with_outliers_no-arcsinh_DREMI_score"] = dremi_with_outliers_no_arc
#             ###### 
            
            # save the info in the dict (df_info_dict) to a dataframe (df_info)             
            df_info = df_info.append(df_info_dict, ignore_index=True)
            
        else: # i.e. outlier removal == True
            
            #####
            # save plots and dremi scores; with outliers
            dremi_with_outliers_no_arc = scprep.stats.knnDREMI(data[marker_x], data[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"{no_arc_marker_comb_drevi_plots_dir}/from_{cell_type}_{cell_state}_cells_x={marker_x}_y={marker_y}_no-arc.png")
            dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], data_arc[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"{arc_marker_comb_drevi_plots_dir}/from_{cell_type}_{cell_state}_cells_x={marker_x}_y={marker_y}_arc.png")
            
            df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc
            df_info_dict["with_outliers_no-arcsinh_DREMI_score"] = dremi_with_outliers_no_arc
            #####    
            
#             ######
#             # save dremi scores if we don't want the plots; with outliers
#             dremi_with_outliers_no_arc = scprep.stats.knnDREMI(data[marker_x], data[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi)
#             dremi_with_outliers_arc = scprep.stats.knnDREMI(data_arc[marker_x], data_arc[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi)
            
#             df_info_dict["with_outliers_arcsinh_DREMI_score"] = dremi_with_outliers_arc
#             df_info_dict["with_outliers_no-arcsinh_DREMI_score"] = dremi_with_outliers_no_arc
#             ###### 

            for cutoff in num_std_for_outliers:
                colname_no_arc = f"wo_outliers_no-arcsinh_cutoff={cutoff}_std_DREMI_score"
                colname_arc = f"wo_outliers_arcsinh_cutoff={cutoff}_std_DREMI_score"
                
                # call the function 'z_score_outliers_removal'
                (data_no_arc_outliers_x, data_no_arc_outliers_y, data_no_arc_only_outliers_xy, data_no_arc_wo_outliers, data_no_arc_num_outliers_x, data_no_arc_num_outliers_y, data_no_arc_num_outliers_total) = z_score_outliers_removal(data, cutoff, marker_x, marker_y)
                (data_arc_outliers_x, data_arc_outliers_y, data_arc_only_outliers_xy, data_arc_wo_outliers, data_arc_num_outliers_x, data_arc_num_outliers_y, data_arc_num_outliers_total) = z_score_outliers_removal(data_arc, cutoff, marker_x, marker_y)
                
                # save plots and dremi scores; wo transformation
                if data_no_arc_num_outliers_total > 0:
                    dremi_wo_outliers_no_arc = scprep.stats.knnDREMI(data_no_arc_wo_outliers[marker_x], data_no_arc_wo_outliers[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"{no_arc_marker_comb_drevi_plots_dir}/from_{cell_type}_{cell_state}_cells_x={marker_x}_y={marker_y}_cutoff={cutoff}_no-arc.png")
#                     dremi_wo_outliers_no_arc = scprep.stats.knnDREMI(data_no_arc_wo_outliers[marker_x], data_no_arc_wo_outliers[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi) # no plots
                    df_info_dict[colname_no_arc] = dremi_wo_outliers_no_arc
                if data_no_arc_num_outliers_total == 0:
                    df_info_dict[colname_no_arc] = "-" # this is a placeholder
                    
                # save plots and dremi scores; arcsinh-transformed
                if data_arc_num_outliers_total > 0:
                    dremi_wo_outliers_arc = scprep.stats.knnDREMI(data_arc_wo_outliers[marker_x], data_arc_wo_outliers[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi, filename=f"{arc_marker_comb_drevi_plots_dir}/from_{cell_type}_{cell_state}_cells_x={marker_x}_y={marker_y}_cutoff={cutoff}_arc.png")
#                     dremi_wo_outliers_arc = scprep.stats.knnDREMI(data_arc_wo_outliers[marker_x], data_arc_wo_outliers[marker_y], k=k, n_bins=n_bins, n_mesh=n_mesh, plot=plot, return_drevi=return_drevi) # no plots
                    df_info_dict[colname_arc] = dremi_wo_outliers_arc
                if data_arc_num_outliers_total == 0:
                    df_info_dict[colname_arc] = "-" # this is a placeholder
                                    
                df_info_dict[f"no-arcsinh_cutoff={cutoff}_num_outliers_x"] = data_no_arc_num_outliers_x
                df_info_dict[f"no-arcsinh_cutoff={cutoff}_num_outliers_y"] = data_no_arc_num_outliers_y
                df_info_dict[f"no-arcsinh_cutoff={cutoff}_num_outliers_total"] = data_no_arc_num_outliers_total

                df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_x"] = data_arc_num_outliers_x
                df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_y"] = data_arc_num_outliers_y
                df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_total"] = data_arc_num_outliers_total
                
            df_info = df_info.append(df_info_dict, ignore_index=True) # save the info in the dict (df_info_dict) to a dataframe (df_info)   

# save info in the dataframe df_info to a txt file
df_info.to_csv(f"{info_dir}/dremi_info.txt", sep="\t")