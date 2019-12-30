import pandas as pd
import numpy as np
import os, sys
from aux_functions import yes_or_NO
from aux_functions import write_panel_emd, read_marker_csv
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

# Input file should 'dremi' in its name
dremi_file = []

for file in os.listdir(input_dir):
    if file.endswith(".txt"):
        if "dremi" in file.lower():
            dremi_file.append(file)
if len(dremi_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'dremi' in its name!")
dremi_file = f"{input_dir}/{dremi_file[0]}"
df = pd.read_csv(dremi_file, sep = '\t')

# create the marker_list csv file if it doesn't exist
# the user needs to specify the markers used for PCA with 'Y' in the file

if marker_list == False:
    sys.exit("ERROR: Please select markers for PCA in the panel_markers.csv file!")

# define the list of markers used for PCA
markers_pca = read_marker_csv(input_dir)

info_run =  input("Write PCA info (using no spaces!): ")

# reformat the data for PCA 
df = df.sort_values(by = ["file_origin"]) 

df_one_cond = pd.DataFrame()
df_all_cond = pd.DataFrame()

row_to_remove = [r for r in df.marker_x if r not in markers_pca]
df = df.loc[~df.marker_x.isin(row_to_remove)]

row_to_remove = [r for r in df.marker_y if r not in markers_pca]
df = df.loc[~df.marker_y.isin(row_to_remove)]

for row in df.iterrows():
    df['x_y'] = df['marker_x'] + '_' + df['marker_y']  

# extract and reformat dremi info
cols_to_keep = ['with_outliers_arcsinh_DREMI_score', 'x_y', 'file_origin']
df = df[cols_to_keep].iloc[:,:].copy()
df = df.rename(columns = {'with_outliers_arcsinh_DREMI_score' : 'DREMI_score'}) 

i = 0 # counter for conditions
conditions = list(df["file_origin"].unique())
for c in conditions:
    name = c
    df_1 = df[df['file_origin'] == c].iloc[:,:].copy()
    df_1 = df_1.rename(columns = {'DREMI_score': f"{name}"}) # use condition names for dremi score column
    keep_cols = ['x_y', f"{name}"]
    df_1 = df_1[keep_cols].iloc[:,:]
    
    if i == 0:
        df_one_cond = df_1.iloc[:,:].copy() # create the output dataframe for the first condition (i == 0)
    else:
        tmp = df_one_cond.merge(df_1, left_on = 'x_y', right_on = 'x_y') # add a new condition to the existing dataframe (merge) (i != 0)
        df_one_cond = tmp.iloc[:,:].copy()
    i += 1

df_all_cond = df_one_cond.iloc[:,:].copy() # if there is only one data file

# change the index to the list of markers and transpose the dataframe
col_to_index = ['x_y']
df_all_cond = df_all_cond.set_index(col_to_index).T

######
### PCA, z-score transformation
######
 
df = df_all_cond.iloc[:,:].copy() # make a copy of the dataframe on with PCA is going to be performed
df_standardized = pd.DataFrame(StandardScaler().fit_transform(df), columns = df.columns, index = df.index) # Standardize features by removing the mean and scaling to unit variance, i.e. z-score

# PCA, z-score
pca = PCA(n_components = 2)
principalComponents = pca.fit_transform(df_standardized)       
explained_variance_ratio = pca.explained_variance_ratio_
principalDf = pd.DataFrame(data = principalComponents, 
                                columns = [f"PC_1 ({explained_variance_ratio[0]*100:.2f}% explained variance)", 
                                        f"PC_2 ({explained_variance_ratio[1]*100:.2f}% explained variance)"])
principalDf["condition"] = list(df_standardized.index)

principalDf.to_csv(f"{output_dir}/dremi-pca_{info_run}.csv", index = False)

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