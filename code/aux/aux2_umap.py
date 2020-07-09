
import pandas as pd
import numpy as np
import umap
import sys
import os

# import warnings
# warnings.filterwarnings('ignore')

# UMAP function
# umap embedding calculation; result saved in a pandas dataframe
# the names of the umap info columns are also defined here

def perform_umap(umap_params, all_together_vs_marks, no_arc, input_files, 
                    output_dir, info_run):
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
                            columns=[f"{run_name}_D1",f"{run_name}_D2"])
    # append umap info columns into untransformed data
    # no_arc[run_name+"_D1"] = umap_emb[run_name+"_D1"]
    # no_arc[run_name+"_D2"] = umap_emb[run_name+"_D2"]
    umap_emb = umap_emb.reset_index(drop=True)
    no_arc = no_arc.reset_index(drop=True)
    no_arc = no_arc.join(umap_emb)

    # #Check if user wants to upload the UMAP info to Cytobank
    # #If yes, generate a 
    # while True:
    #     convert = input("Prepare txt files for Cytobank upload? (Y/N): ")
    #     if convert not in ('Y', 'N', 'y', 'n'):
    #         continue
    #     else:
    #         break
        
    #Write merged file and individual files with UMAP dimensions

    if len(set(no_arc["file_origin"])) > 1: # more than one file
        whole_file = "merged_" + run_name
        no_arc.to_csv(f"{output_dir}/{info_run}/{whole_file}.txt", 
                        index = False, sep = '\t')

    for i in input_files: #Split merged file by file_origin->
        file_origin = i.split('.')[0] #>- allows to import conditions to cytobank
        partial_file = file_origin + "_" + run_name
        no_arc.loc[no_arc["file_identifier"] == file_origin,:].to_csv(
            f"{output_dir}/{info_run}/{partial_file}.txt", index = False,
            sep = '\t')

            