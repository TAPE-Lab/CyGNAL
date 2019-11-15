
import pandas as pd
import numpy as np
from aux_functions import arcsinh_transf
import scprep
import sys
import os

# Function to calculate EMD

def calculate_emd(marker_list, emd_infodict, compare_from, compare_to,
                    normalisation, emd_df):
    for marker in marker_list:
        emd_infodict["marker"] = marker
        emd_infodict[f"median_{normalisation}_arc_compare_from"
                        ] = compare_from[marker].median()
        emd_infodict[f"median_{normalisation}_arc_compare_to"
                        ] = compare_to[marker].median()
        emd_infodict[f"median_diff_{normalisation}_arc_compare_from_vs_to"
                        ] = compare_from[marker].median() - compare_to[
                                                            marker].median()
        #As the distance calculated is a positve value, change to negative 
        # if input has smaller median than the denominator
        if (compare_from[marker].median() - compare_to[marker].median()) >= 0:
            emd_infodict[f"EMD_{normalisation}_arc"] = scprep.stats.EMD(
                                                        compare_from[marker],
                                                        compare_to[marker])
        else:
            emd_infodict[f"EMD_{normalisation}_arc"] = -scprep.stats.EMD(
                                                        compare_from[marker],
                                                        compare_to[marker])
        #Add EMD score to the output dataframe
        emd_df = emd_df.append(emd_infodict, ignore_index=True)
    
    return emd_df

def downsample_data(no_arc, info_run, output_dir):
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
    new_df.to_csv(f"{output_dir}/{info_run}_downsampled_IDs.csv", 
                    index = False)
    no_arc = no_arc[no_arc["Sample_ID-Cell_Index"].isin(reduced_df["Sample_ID-Cell_Index"])]
    return reduced_df
    