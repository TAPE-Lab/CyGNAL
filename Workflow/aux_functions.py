
import pandas as pd
import numpy as np
import umap
import sys
import os

#Function to concatenate all files
def concatenate_fcs(folder_name):
    input_files = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]
    no_arc = pd.DataFrame()
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for file in input_files:
        fcounter += 1
        df = pd.read_csv(f"{folder_name}/{file}", sep = '\t')
        df["file_origin"] = str(fcounter)+" | "+ file # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        no_arc = no_arc.append(df, ignore_index=True)
    return no_arc, input_files

#Arcsinh transform the data
def arcsinh_transf(cofactor, no_arc):
    #Select only the columns containing the markers (as they start with a number for the isotope)
    cols = [x for x in no_arc.columns if x[0].isdigit()]
    #Apply the arcsinh only to those columns (don't want to change time or any other)
    arc = no_arc.apply(lambda x: np.arcsinh(x/cofactor) if x.name in cols else x)
    # put back the 'file_origin' column to the arcsinh-transformed data
    arc["file_origin"] = no_arc["file_origin"]
    return arc, cols

# Random downsampling of a dataframe to n rows
def downsample_df(df, n):
    df_downsampled = df.sample(n)
    return df_downsampled