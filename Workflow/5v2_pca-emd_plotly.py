import pandas as pd
import numpy as np
import os, sys
from aux_functions import yes_or_NO
from aux_functions import write_panel_emd
from aux2_umap import identify_markers
import plotly.express as px

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "5v2-pca"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There was no input folder!") 
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"

### User Input ### 
# emd = yes_or_NO("Perform PCA on the EMD scores?")
# dremi = yes_or_NO("Perform PCA on the DREMI scores?")
marker_list = yes_or_NO("Markers for PCA selected?")

# Input file should have 'emd' its name
emd_file = []

for file in os.listdir(input_dir):
    if file.endswith(".txt"):
        if "emd" in file.lower():
            emd_file.append(file)
if len(emd_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'emd' in its name!")
emd_file = f"{input_dir}/{emd_file[0]}"
df = pd.read_csv(emd_file, sep = '\t')

# create the marker_list csv file if it doesn't exist
# the user needs to specify the markers used for PCA with 'Y' in the file

if marker_list == False:
    write_panel_emd(df, input_dir)
    sys.exit("ERROR: Please select markers for PCA in the panel_markers.csv file!")

# define the list of markers used for PCA
marker_file = pd.read_csv(f"{input_dir}/panel_markers.csv", header = None)
markers_pca = identify_markers(marker_file)

info_run =  input("Write PCA info (using no spaces!): ")

# reformat the data for PCA 
df = df.sort_values(by = ["file_origin"]) 

df_one_cond = pd.DataFrame()
df_all_cond = pd.DataFrame()

# extract and reformat emd info
cols_to_keep = ["EMD_no_norm_arc", "marker", "file_origin"]
df = df[cols_to_keep].iloc[:,:].copy()
df = df.rename(columns = {"EMD_no_norm_arc" : "EMD_score"}) 

i = 0 # counter for conditions
# extract and reformat emd info -> keep only marker and emd score columns

conditions = list(df["file_origin"].unique())
for c in conditions:
    name = c
    df_1 = df[df["file_origin"] == c].iloc[:,:].copy()
    df_1 = df_1.rename(columns = {"EMD_score": f"{name}"}) # use condition names for emd score column
    keep_cols = ["marker", f"{name}"]
    df_1 = df_1[keep_cols].iloc[:,:]
    
    if i == 0:
        df_one_cond = df_1.iloc[:,:].copy() # create the output dataframe for the first condition (i == 0)
    else:
        tmp = df_one_cond.merge(df_1, left_on = "marker", right_on = "marker") # add a new condition to the existing dataframe (merge) (i != 0)
        df_one_cond = tmp.iloc[:,:].copy()
    i += 1

df_all_cond = df_one_cond.iloc[:,:].copy() # if there is only one data file
df_all_cond = df_all_cond.set_index("marker").T # change the index to the list of markers and transpose the dataframe

cols_to_keep = [c for c in df_all_cond.columns.values if c in markers_pca]
df_all_cond = df_all_cond[cols_to_keep].iloc[:,:]

######
### PCA, z-score transformation
######
 
df = df_all_cond.iloc[:,:].copy() # make a copy of the dataframe on with PCA is going to be performed
df_standardized = pd.DataFrame(StandardScaler().fit_transform(df), 
                    columns = df.columns, index = df.index) 
    # Standardize features by removing the mean and scaling to unit variance, i.e. z-score

# PCA, z-score
pca = PCA(n_components = 2)
principalComponents = pca.fit_transform(df_standardized)       
explained_variance_ratio = pca.explained_variance_ratio_
principalDf = pd.DataFrame(data = principalComponents, 
                                columns = [f"PC_1 ({explained_variance_ratio[0]*100:.2f}% explained variance)", 
                                        f"PC_2 ({explained_variance_ratio[1]*100:.2f}% explained variance)"])
principalDf["condition"] = list(df_standardized.index)

principalDf.to_csv(f"{output_dir}/emd-pca_{info_run}.csv", index = False)

######
### Interactive PCA with plotly
######

fig = px.scatter(principalDf, 
                x=principalDf.columns[0], 
                y=principalDf.columns[1],
                color=principalDf.columns[2],
                hover_name=principalDf.columns[2])

fig.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))

fig.show()