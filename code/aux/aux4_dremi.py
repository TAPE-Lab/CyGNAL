
import os
import sys
from itertools import permutations

import numpy as np
import pandas as pd
import scprep


# EXPERIMENTAL #
# find outliers for both marker_x and marker_y based on cufoffs of standard deviations
# return the number of outliers and a dataframe after outlier removal
# update the df_info_dict with the number of outliers
#The function identifies outliers based on the absolute difference between each marker's value and its mean, normalized by the marker's standard deviation. Rows that have values exceeding the cutoff multiplied by the standard deviation are considered outliers.
def outlier_removal(df, cutoff, marker_x, marker_y, df_info_dict):
    """
    Removes outliers from a DataFrame based on a cutoff value and specific markers.

    Args:
        df (DataFrame): Input DataFrame.
        cutoff (float): Cutoff value for outlier removal.
        marker_x (str): Marker column name for x-axis.
        marker_y (str): Marker column name for y-axis.
        df_info_dict (dict): Dictionary to store outlier information.

    Returns:
        tuple: A tuple containing the number of total outliers removed and the DataFrame without outliers.
    """
    num_outliers_total = 0
    num_outliers_x = 0
    num_outliers_y = 0
    
    df_outliers_x = df[(np.abs(df[marker_x]-df[marker_x].mean()) > (
                                                    cutoff*df[marker_x].std()))]
    df_outliers_y = df[(np.abs(df[marker_y]-df[marker_y].mean()) > (
                                                    cutoff*df[marker_y].std()))]
    num_outliers_x += df_outliers_x.shape[0]
    num_outliers_y += df_outliers_y.shape[0]
    
    df_wo_outliers = df[(np.abs(df[marker_x]-df[marker_x].mean()) <= (
                                                        cutoff*df[marker_x].std())
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

