
import pandas as pd
import numpy as np
import scprep
import sys
import os
from itertools import permutations



# find outliers for both marker_x and marker_y based on cufoffs of standard deviations
# return the number of outliers and a dataframe after outlier removal
# update the df_info_dict with the number of outliers
def outlier_removal(df, cutoff, marker_x, marker_y, df_info_dict):
    num_outliers_total = 0
    num_outliers_x = 0
    num_outliers_y = 0
    
    df_outliers_x = df[(np.abs(df[marker_x]-df[marker_x].mean()) > (cutoff*df[marker_x].std()))]
    df_outliers_y = df[(np.abs(df[marker_y]-df[marker_y].mean()) > (cutoff*df[marker_y].std()))]
    num_outliers_x += df_outliers_x.shape[0]
    num_outliers_y += df_outliers_y.shape[0]
    
    df_wo_outliers = df[(np.abs(df[marker_x]-df[marker_x].mean()) <= (cutoff*df[marker_x].std())
                            ) & (np.abs(df[marker_y]-df[marker_y].mean()
                            ) <= (cutoff*df[marker_y].std()))]
    df_only_outliers_xy = df[(np.abs(df[marker_x]-df[marker_x].mean()) > (
                                cutoff*df[marker_x].std())) | (np.abs(
                                    df[marker_y]-df[marker_y].mean()) > (
                                        cutoff*df[marker_y].std()))]
    num_outliers_total += df_only_outliers_xy.shape[0]

    # Update the df_info_dict dictionary with outlier info
    df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_x"] = num_outliers_x
    df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_y"] = num_outliers_y
    df_info_dict[f"arcsinh_cutoff={cutoff}_num_outliers_total"] = num_outliers_total

    return(num_outliers_total, df_wo_outliers)

