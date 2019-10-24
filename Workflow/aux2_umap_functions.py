
import pandas as pd
import numpy as np
import umap
import sys
import os

# import warnings
# warnings.filterwarnings('ignore')


#Downsampling the data to equate fil_origin sizes
def downsample_data(no_arc, info_run):
    downsampled_dframe = no_arc.copy()
    #Defiine downsampling size (N) per file:
    downsample_size = downsampled_dframe["file_origin"].value_counts().min() #at least N cells in all input files
    print ("Working with ", downsample_size, " cells per file_origin")
    #Group by file+origin and sample without replacement -> 
    # thus we can sample file for which len(file)=N without -tive consequences
    
    reduced_df = downsampled_dframe.groupby("file_origin").apply(lambda x:
                                                    x.sample(downsample_size))
    
    #Create new file to store downsampling status for all cell IDs
    new_df = pd.DataFrame()
    new_df["Sample_ID-Cell_Index"] = no_arc["Sample_ID-Cell_Index"]
    new_df["In_donwsampled_file"] = new_df["Sample_ID-Cell_Index"].isin(
                                        reduced_df["Sample_ID-Cell_Index"])
    new_df.to_csv(f"./output/2-umap/{info_run}_downsampled_IDs.csv", 
                    index = False)
    no_arc = no_arc[no_arc["Sample_ID-Cell_Index"].isin(reduced_df["Sample_ID-Cell_Index"])]
    return reduced_df


#Arcsinh transform the data
def arcsinh_transf(cofactor, no_arc):
    arc = no_arc.iloc[:,:-1] #leave out the last column ('file_origin')
    #Select only the columns containing the markers (as they start with a number for the isotope)
    cols = [x for x in arc.columns if x[0].isdigit()]
    #Apply the arcsinh only to those columns (don't want to change time or any other)
    arc = arc.apply(lambda x: np.arcsinh(x/cofactor) if x.name in cols else x)
    # put back the 'file_origin' column to the arcsinh-transformed data
    arc["file_origin"] = no_arc["file_origin"]
    return arc, cols

#Get markers flagged for use
def identify_markers(marker_file):
    markers_umap = marker_file.loc[marker_file[1] == "Y", [0]].values.tolist()
    markers_umap = [item for sublist in markers_umap for item in sublist] #Flatten list
    return markers_umap

# UMAP function
# umap embedding calculation; result saved in a pandas dataframe
# the names of the umap info columns are also defined here
def perform_umap(umap_params, all_together_vs_marks, arc, input_files):
    info_run = umap_params["info"]
    run_name = "UMAP_"+info_run
    #Calculate UMAP on arc tranf data (all_together...)
    umap_emb = pd.DataFrame(umap.UMAP(n_neighbors=umap_params["n"], 
                                min_dist=umap_params["m"],
                                metric=umap_params["d"],
                                n_components=umap_params["comp"],
                                repulsion_strength=umap_params["rs"],
                                negative_sample_rate=umap_params["nsr"]
                            ).fit_transform(all_together_vs_marks), 
                            columns=[run_name+"_D1",run_name+"_D2"])
    # append umap info columns into untransformed data
    # no_arc[run_name+"_D1"] = umap_emb[run_name+"_D1"]
    # no_arc[run_name+"_D2"] = umap_emb[run_name+"_D2"]
    umap_emb = umap_emb.reset_index(drop=True)
    arc = arc.reset_index(drop=True)
    arc = arc.join(umap_emb)

    # #Check if user wants to upload the UMAP info to Cytobank
    # #If yes, generate a 
    # while True:
    #     convert = input("Prepare txt files for Cytobank upload? (Y/N): ")
    #     if convert not in ('Y', 'N', 'y', 'n'):
    #         continue
    #     else:
    #         break
        
    #Write merged file and individual files with UMAP dimensions
    if len(set(arc["file_origin"])) > 1: # more than one file
        whole_file = "merged_" + run_name
        arc.to_csv(f"./output/2-umap/{whole_file}.txt", index = False,
                        sep = '\t')

    for i in input_files:
        partial_file = i + "_" + run_name
        arc.loc[arc["file_origin"].str.endswith(i),:].to_csv(
            f"./output/2-umap/{partial_file}.txt", index = False, sep = '\t')

            