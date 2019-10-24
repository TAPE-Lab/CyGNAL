
import pandas as pd
import numpy as np
import umap
import sys
import os

import warnings
warnings.filterwarnings('ignore')

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
        df["Sample_ID-Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID #This way the cell-index will be preserved after Cytobank upload
        # df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        no_arc = no_arc.append(df, ignore_index=True)
    return no_arc, input_files

# Random downsampling of a dataframe to n rows
def downsample_df(df, n):
    df_downsampled = df.sample(n)
    return df_downsampled

#Function to concatenate all files and save as txt 
def concatenate_save(folder_name):
    input_files = [f for f in os.listdir(f"./{folder_name}") if f.endswith(".txt")]
    concat = pd.DataFrame()
    #Add counter to keep track of the number of files in input -> 
    # -> cell ID will be a mix of these (Filenumber | filename.txt)
    fcounter = 0
    for file in input_files:
        name = file.split('.txt')[0]
        fcounter += 1
        df = pd.read_csv(f"{folder_name}/{file}", sep = '\t')
        df["file_origin"] = str(fcounter)+" | "+ file # add a new column of 'file_origin' that will be used to separate each file after umap calculation
        df["Sample_ID-Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID #This way the cell-index will be preserved after Cytobank upload
        # df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
        concat = concat.append(df, ignore_index=True)

    print("Concatenating...")
    concat.to_csv(f'./output/opt1_concatenation/concat_{name}.txt', index = False, sep = '\t')
    print(f"Concatenated file saved as:\nconcat_{name}.txt")