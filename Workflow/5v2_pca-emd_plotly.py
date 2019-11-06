import pandas as pd
import numpy as np
import os, sys
from aux_functions import yes_or_NO
from aux_functions import write_panel
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
marker = yes_or_NO("Markers for PCA selected?")

#Input files should have either emd or dremi on their name
# if emd==True:
emd_file = []

for file in os.listdir(input_dir):
    if file.endswith(".txt"):
        if "emd" in file.lower():
            emd_file.append(file)
if len(emd_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'emd' in its name!")
emd_file = f"{input_dir}/{emd_file[0]}"

#
if marker == False:
    write_panel(emd_file)
    sys.exit("ERROR: Please select markers for PCA in the panel_markers.csv file!")

# reformat the data for PCA

d = {}

for m in markers:
    
    df_markers = pd.read_csv(os.path.join(markers_dir, m), sep = "\t")
    markers_to_keep = list(df_markers["marker"])
    
    df_one_cell_type_all_conds = pd.DataFrame()
    df_all_cell_types_all_conds = pd.DataFrame()
    
    j = 0 # counter for files (one data file per cell type)
    
    for f in files:

        df = pd.read_csv(os.path.join(files_dir, f), sep = "\t")
        df = df.sort_values(by = ["compare_from"]) 
        print(df.shape)
        
        # extract and reformat emd info
        cols_to_keep_1 = ["EMD_no_norm_arc", "marker", "compare_from", "compare_to"]
        df = df[cols_to_keep_1].iloc[:,:].copy()
        df = df.rename(columns = {"EMD_no_norm_arc" : "EMD_score"}) 
        cols_to_keep_2 = ["marker", "compare_from", "EMD_score"]
        df = df[cols_to_keep_2].iloc[:,:]
        
        i = 0 # counter for conditions
        # extract and reformat emd info -> keep only marker and emd score columns
        
        conditions = list(df["compare_from"].unique())
        for c in conditions:
            name = c
            df_1 = df[df["compare_from"] == c].iloc[:,:].copy()
            df_1 = df_1.rename(columns = {"EMD_score": f"{name}"}) # use condition names for emd score column
            keep_cols = ["marker", f"{name}"]
            df_1 = df_1[keep_cols].iloc[:,:]
            
            if i == 0:
                df_one_cell_type_all_conds = df_1.iloc[:,:].copy() # create the output dataframe for the first condition (i == 0)
            else:
                tmp = df_one_cell_type_all_conds.merge(df_1, left_on = "marker", right_on = "marker") # add a new condition to the existing dataframe (merge) (i != 0)
                df_one_cell_type_all_conds = tmp.iloc[:,:].copy()
            i += 1

        if j == 0:
            df_all_cell_types_all_conds = df_one_cell_type_all_conds.iloc[:,:].copy() # if there is only one data file
        else:
            tmp = df_all_cell_types_all_conds.merge(df_one_cell_type_all_conds, left_on = "marker", right_on = "marker")
            df_all_cell_types_all_conds = tmp.iloc[:,:].copy()
            
        j += 1          

    # change the index to the list of markers and transpose the dataframe
    col_to_index = ["marker"]
    df_all_cell_types_all_conds = df_all_cell_types_all_conds.set_index(col_to_index).T

    # save the result dataframe to the dictionary 'd', one key per marker list
    d[m] = df_all_cell_types_all_conds
    d[m].head()


# %%
# PCA, z-score transformation

for k,v in d.items():
#     print(k)
    
    df = v.iloc[:,:].copy() # make a copy of the dataframe on with PCA is going to be performed
    df_standardized = pd.DataFrame(StandardScaler().fit_transform(df), columns = df.columns, index = df.index) # Standardize features by removing the mean and scaling to unit variance, i.e. z-score
    
    # PCA, z-score
    pca = PCA(n_components = 2)
    principalComponents = pca.fit_transform(df_standardized)       
    explained_variance_ratio = pca.explained_variance_ratio_
    principalDf = pd.DataFrame(data = principalComponents, 
                                 columns = [f"PC_1 ({explained_variance_ratio[0]*100:.0f}% explained variance)", 
                                            f"PC_2 ({explained_variance_ratio[1]*100:.0f}% explained variance)"])
    principalDf["condition"] = list(df_standardized.index)

principalDf.to_csv("pca_figure-1_demo.csv", index = False)

# %%
principalDf.head()

fig = px.scatter(principalDf, 
                x=principalDf.columns[0], 
                y=principalDf.columns[1],
                color=principalDf.columns[2],
                hover_name=df.columns[2])

fig.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))

fig.show()

# # %% [markdown]
# # ### DREMI

# # %%
# df_markers = pd.read_csv(os.path.join(markers_dir, '27-markers-for-pca.txt'), sep = "\t")
# markers_to_keep = list(df_markers["marker"])
# markers_to_keep


# # %%
# # reformat the data for PCA (dremi)

# d = {}

# for m in markers:
    
#     df_markers = pd.read_csv(os.path.join(markers_dir, m), sep = "\t")
#     markers_to_keep = list(df_markers["marker"])
    
#     df_one_cell_type_all_conds = pd.DataFrame()
#     df_all_cell_types_all_conds = pd.DataFrame()
    
#     j = 0 # counter for files (one data file per cell type)
    
#     for f in files:

#         df = pd.read_csv(os.path.join(files_dir, f), sep = "\t", index_col = 0)
#         df = df.sort_values(by = ['file']) # check this
#         print(df.shape)
        
#         # make a new column for 'x_y' DREMI pairs
#         for row in df.iterrows():
#             df['x_y'] = df['marker_x'] + '_' + df['marker_y']  
        
#         # extract and reformat dremi info
#         cols_to_keep_1 = ['with_outliers_arcsinh_DREMI_score', 'x_y', 'file']
#         df = df[cols_to_keep_1].iloc[:,:].copy()
#         df = df.rename(columns = {'with_outliers_arcsinh_DREMI_score' : 'DREMI_score'}) 
#         cols_to_keep_2 = ['x_y', 'file', 'DREMI_score']
#         df = df[cols_to_keep_2].iloc[:,:]
        
#         i = 0 # counter for conditions
#         # extract and reformat emd info -> keep onely marker and dremi score columns
        
#         conditions = list(df['file'].unique())
#         for c in conditions:
#             name = c.split('.')[0]
#             df_1 = df[df['file'] == c].iloc[:,:].copy()
#             df_1 = df_1.rename(columns = {'DREMI_score': f"{name}"}) # use condition names for dremi score column
#             keep_cols = ['x_y', f"{name}"]
#             df_1 = df_1[keep_cols].iloc[:,:]
            
#             if i == 0:
#                 df_one_cell_type_all_conds = df_1.iloc[:,:].copy() # create the output dataframe for the first condition (i == 0)
#             else:
#                 tmp = df_one_cell_type_all_conds.merge(df_1, left_on = 'x_y', right_on = 'x_y') # add a new condition to the existing dataframe (merge) (i != 0)
#                 df_one_cell_type_all_conds = tmp.iloc[:,:].copy()
#             i += 1

#         if j == 0:
#             df_all_cell_types_all_conds = df_one_cell_type_all_conds.iloc[:,:].copy() # if there is only one data file (one cell type)
#         else:
#             tmp = df_all_cell_types_all_conds.merge(df_one_cell_type_all_conds, left_on = 'x_y', right_on = 'x_y')
#             df_all_cell_types_all_conds = tmp.iloc[:,:].copy()
            
#         j += 1          

#     # change the index to the list of markers and transpose the dataframe
#     col_to_index = ['x_y']
#     df_all_cell_types_all_conds = df_all_cell_types_all_conds.set_index(col_to_index).T

#     # save the result to the dictionary 'd', one key per marker list
#     d[m] = df_all_cell_types_all_conds
#     d[m].head()


# # %%
# # PCA, no-normalisation and z-score

# raw = {}
# zscore = {}

# for k,v in d.items():
# #     print(k)
    
#     df = v.iloc[:,:].copy() # make a copy of the dataframe on with PCA is going to be performed
#     df_standardized = pd.DataFrame(StandardScaler().fit_transform(df), columns = df.columns, index = df.index) # Standardize features by removing the mean and scaling to unit variance, i.e. z-score
    
#     # PCA, no-normalisation
#     pca = PCA(n_components = 2)
#     principalComponents = pca.fit_transform(df)       
#     explained_variance_ratio = pca.explained_variance_ratio_
#     principalDf = pd.DataFrame(data = principalComponents, 
#                                columns = [f"PC_1 ({explained_variance_ratio[0]*100:.2f}% explained variance)", 
#                                           f"PC_2 ({explained_variance_ratio[1]*100:.2f}% explained variance)"])
#     principalDf["condition"] = list(df.index)
#     raw[k] = principalDf
    
#     # PCA, z-score
#     pca_2 = PCA(n_components = 2)
#     principalComponents_2 = pca_2.fit_transform(df_standardized)       
#     explained_variance_ratio_2 = pca_2.explained_variance_ratio_
#     principalDf_2 = pd.DataFrame(data = principalComponents_2, 
#                                  columns = [f"PC_1 ({explained_variance_ratio_2[0]*100:.2f}% explained variance)", 
#                                             f"PC_2 ({explained_variance_ratio_2[1]*100:.2f}% explained variance)"])
#     principalDf_2["condition"] = list(df_standardized.index)
#     zscore[k] = principalDf_2   