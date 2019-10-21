
import pandas as pd
import numpy as np
import umap
import sys
import os

import warnings
warnings.filterwarnings('ignore')

#Function to concatenate all files
def concatenate_fcs(folder_name):
    filenames_no_arcsinh = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]
    no_arc = pd.DataFrame()
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for file in filenames_no_arcsinh:
        fcounter += 1
        df = pd.read_csv(f"{folder_name}/{file}", sep = '\t')
        df["file_origin"] = str(fcounter)+" | "+ file # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        no_arc = no_arc.append(df, ignore_index=True)
    return no_arc, filenames_no_arcsinh

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
def perform_umap(umap_params, all_together_vs_marks, no_arc, input_files):
    info_run = umap_params["info"]
    run_name = "UMAP_"+info_run
    #Calculate UMAP on arc tranf data (all_together...)
    umap_emb = pd.DataFrame(umap.UMAP(n_neighbors=umap_params["n"], min_dist=umap_params["m"],
                metric=umap_params["d"], n_components=umap_params["comp"],
                repulsion_strength=umap_params["rs"],
                negative_sample_rate=umap_params["nsr"]).fit_transform(all_together_vs_marks), 
                    columns=[run_name+"_D1",run_name+"_D2"])
    # append umap info columns into untransformed data
    no_arc[run_name+"_D1"] = umap_emb[run_name+"_D1"]
    no_arc[run_name+"_D2"] = umap_emb[run_name+"_D2"]
    
    #Write merged file and individual files with UMAP dimensions
    whole_file = "merged_" + info_run
    no_arc.to_csv(f"./output/2-umap/{whole_file}.txt", index = False, sep = '\t')
    for i in input_files:
        partial_file = i +"__" + info_run
        no_arc.loc[no_arc["file_origin"].str.endswith(input_files[0]),:].to_csv(f"./output/2-umap/{partial_file}.txt", index = False, sep = '\t')

