
import pandas as pd
import numpy as np
import scprep
import sys
import os

# Function to calculate EMD
# calculate emd and sign the emd score by the difference of median between compare_from and compare_to
def emd_arc(data_from_arc, data_to_arc, marker, normalisation):
    
    df_info_dict[f"median_{normalisation}_arc_compare_from"] = data_from_arc[marker].median()
    df_info_dict[f"median_{normalisation}_arc_compare_to"] = data_to_arc[marker].median()
    df_info_dict[f"median_diff_{normalisation}_arc_compare_from_vs_to"] = data_from_arc[marker].median() - data_to_arc[marker].median()
    
    if (data_from_arc[marker].median() - data_to_arc[marker].median()) >= 0:
        emd_arc = scprep.stats.EMD(data_from_arc[m], data_to_arc[m])
    if (data_from_arc[marker].median() - data_to_arc[marker].median()) < 0:
        emd_arc = -scprep.stats.EMD(data_from_arc[m], data_to_arc[m])

    
    return emd_arc
