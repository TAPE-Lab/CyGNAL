
import pandas as pd
import numpy as np
from aux_functions import arcsinh_transf
import scprep
import sys
import os

# Function to calculate EMD

def calculate_emd(marker_list, emd_infodict, compare_from, compare_to, normalisation, emd_df):
    for marker in marker_list:
        emd_infodict["marker"] = marker
        emd_infodict[f"median_{normalisation}_arc_compare_from"] = compare_from[marker].median()
        emd_infodict[f"median_{normalisation}_arc_compare_to"] = compare_to[marker].median()
        emd_infodict[f"median_diff_{normalisation}_arc_compare_from_vs_to"] = compare_from[marker].median() - compare_to[marker].median()
        #As the distance calculated is a positve value, change to negative if input has smaller median than the denominator
        if (compare_from[marker].median() - compare_to[marker].median()) >= 0:
            emd_infodict[f"EMD_{normalisation}_arc"] = scprep.stats.EMD(compare_from[marker], compare_to[marker])
        else:
            emd_infodict[f"EMD_{normalisation}_arc"] = -scprep.stats.EMD(compare_from[marker], compare_to[marker])
        #Add EMD score to the output dataframe
        emd_df = emd_df.append(emd_infodict, ignore_index=True)
    
    return emd_df

# # calculate emd and sign the emd score by the difference of median between compare_from and compare_to
# def emd_scores(compare_from, compare_to, markers_compare_to, normalisation):
#     for marker in markers_compare_to:
#         emd_infodict["marker"] = marker
        
        
#         emd_infodict[f"EMD_{normalisation}_arc"] = emd_scores(compare_from, )
#         df_info_dict[f"median_{normalisation}_arc_compare_from"] = compare_from[marker].median()
#         df_info_dict[f"median_{normalisation}_arc_compare_to"] = compare_to[marker].median()
#         df_info_dict[f"median_diff_{normalisation}_arc_compare_from_vs_to"] = compare_from[marker].median() - compare_to[marker].median()
#         #As the distance calculated is a positve value, change to negative if input has smaller median than the denominator
#         if (compare_from[marker].median() - compare_to[marker].median()) >= 0:
#             emd_arc = scprep.stats.EMD(compare_from[marker], compare_to[marker])
#         if (compare_from[marker].median() - compare_to[marker].median()) < 0:
#             emd_arc = -scprep.stats.EMD(compare_from[marker], compare_to[marker])

#     return emd_arc


# def calculate_emd(info_run, input_files, folder_name, markers_compare_to, normalisation, compare):
#     emd_df = pd.DataFrame()
#     emd_infodict = {}
#     emd_infodict["denominator"]=info_run
#     for compare_from_file in input_files:
#         emd_infodict["file_origin"] = compare_from_file
#         compare_from = pd.read_csv(f"{folder_name}/{compare_from_file}", sep = '\t')
        
#         for marker in markers_compare_to:
#             emd_infodict["marker"] = marker
#             emd_infodict[f"EMD_{normalisation}_arc"] = emd_scores(compare_from, )