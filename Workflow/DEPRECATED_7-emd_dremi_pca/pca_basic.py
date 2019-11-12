# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), '../../../../../../var/folders/hw/fqkcybzs3gq_bksy6wfr534m0000gr/T'))
	print(os.getcwd())
except:
	pass

#%%
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict
import umap

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import holoviews as hv
from IPython.core.interactiveshell import InteractiveShell


#%%
# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"


#%%
current_dir = os.getcwd()
current_dir

# dremi and emd info files are saved in 'data/dremi' and 'data/emd' folders; one file per folder
# list of markers to be used (txt files) for dremi and emd are saved in the same manner in the 'markers_to_use' folder
folder_1 = "data"
# folder_2 = "dremi"
folder_2 = "emd"
markers_folder = "markers_to_use"

files_dir = os.path.join(current_dir, folder_1, folder_2)
markers_dir = os.path.join(current_dir, markers_folder, folder_2)

files_dir
markers_dir

# read in the files and markers to use

files = [file for file in os.listdir(files_dir) if file.endswith(".txt") ]
markers = [file for file in os.listdir(markers_dir) if file.endswith(".txt")]

files
markers

#%% [markdown]
# ### EMD

#%%
# denominator for emd
denominator = "ungated_all-event_1002007-cells" 
denominator


#%%
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


#%%
# PCA, no-normalisation and z-score

raw = {}
zscore = {}

for k,v in d.items():
#     print(k)
    
    df = v.iloc[:,:].copy() # make a copy of the dataframe on with PCA is going to be performed
    df_standardized = pd.DataFrame(StandardScaler().fit_transform(df), columns = df.columns, index = df.index) # Standardize features by removing the mean and scaling to unit variance, i.e. z-score
    
    # PCA, no-normalisation
    pca = PCA(n_components = 2)
    principalComponents = pca.fit_transform(df)       
    explained_variance_ratio = pca.explained_variance_ratio_
    principalDf = pd.DataFrame(data = principalComponents, 
                               columns = [f"PC_1 ({explained_variance_ratio[0]*100:.2f}% explained variance)", 
                                          f"PC_2 ({explained_variance_ratio[1]*100:.2f}% explained variance)"])
    principalDf["condition"] = list(df.index)
    raw[k] = principalDf
    
    # PCA, z-score
    pca_2 = PCA(n_components = 2)
    principalComponents_2 = pca_2.fit_transform(df_standardized)       
    explained_variance_ratio_2 = pca_2.explained_variance_ratio_
    principalDf_2 = pd.DataFrame(data = principalComponents_2, 
                                 columns = [f"PC_1 ({explained_variance_ratio_2[0]*100:.2f}% explained variance)", 
                                            f"PC_2 ({explained_variance_ratio_2[1]*100:.2f}% explained variance)"])
    principalDf_2["condition"] = list(df_standardized.index)
    zscore[k] = principalDf_2   


#%%
principalDf_2.to_csv("pca_figure-1_demo.txt", sep = "\t", index = False)


#%%



#%%



#%%



#%%
# create a colour mapping scheme for pca plots
# or read in an existing colour mapping profile
########## unique to each experiment ##########

make_new_colour_mapping = True
colourmapping_file = "populations_to-colour-and-marker_mapping.txt"

# get the list of the conditions in the dataset
df = pd.read_csv(os.path.join(files_dir, files[0]), sep = "\t")
all_conditions = list(df["compare_from"].unique())
all_conditions


populations_to_colour_mapping = {}
subpopulations_to_marker_mapping = {}
    
if make_new_colour_mapping == True:
    
    # create colour palette
    unique_populations = list(set([x.split("_")[0] for x in all_conditions])) # this needs a bit of design... how do you like to colour the data points on the PCA plots?
    colours_populations = sns.color_palette(n_colors = len(unique_populations)).as_hex()

    # assign colours
    for (a,b) in zip(unique_populations, colours_populations): # zip: make an iterator that aggregates elements from each of the iterables.
        for condition in all_conditions:
            if condition.startswith(a):
                populations_to_colour_mapping[condition] = b  
    
    # assign shapes/markers
    # 
    for condition in all_conditions:
        if "pRB-, CD44-" in condition:
            subpopulations_to_marker_mapping[condition] = "v"
        elif "pRB+, CD44+" in condition:
            subpopulations_to_marker_mapping[condition] = "^" 
        elif "pRB-, CD44+" in condition:
            subpopulations_to_marker_mapping[condition] = "s" 
        elif "pRB+, CD44-" in condition:
            subpopulations_to_marker_mapping[condition] = "D"  
        else:
            subpopulations_to_marker_mapping[condition] = "o"
    
    # 
    df = pd.DataFrame()
    populations = list(populations_to_colour_mapping.keys())
    colours = [populations_to_colour_mapping[x] for x in populations]
    markers = [subpopulations_to_marker_mapping[x] for x in populations]
    df["populations"] = populations
    df["colour_codes"] = colours
    df["markers"] = markers
    
    df.to_csv("populations_to-colour-and-marker_mapping.txt", sep="\t")
    
else:
    df = pd.read_csv(colourmapping_file, sep = "\t")
    for i in df.index:
        populations_to_colour_mapping[df.iloc[i]["populations"]] = df.iloc[i]["colour_codes"]
        subpopulations_to_marker_mapping[df.iloc[i]["populations"]] = df.iloc[i]["markers"]


#%%
populations_to_colour_mapping


#%%
subpopulations_to_marker_mapping


#%%
all_conditions


#%%
# save pca result and plots (no normalisation)

for k,v in raw.items():
    name = k.split(".")[0]
    df = v.iloc[:,:].copy() # make a copy of the dataframe with PCA info (no-normalisation)
        
    df["colour"] = df['condition'].map(populations_to_colour_mapping)
    df["marker_plot"] = df['condition'].map(subpopulations_to_marker_mapping)
    
    # save coordinates
    df.to_csv(f"./output/data/denominator={denominator}_{name}_no-normalization.txt", sep="\t")
    
    x_name = [col for col in list(df.columns) if col.startswith("PC_1")][0]
    y_name = [col for col in list(df.columns) if col.startswith("PC_2")][0]
    hue = [col for col in list(df.columns) if not col.startswith("PC_")][0]
    
    # save plots
    all_plot_ = []
    for j in df.index:
        plot = plt.scatter(x = df.iloc[j][x_name], y = df.iloc[j][y_name], c = df.iloc[j]["colour"], marker = df.iloc[j]["marker_plot"], s = 200)
        all_plot_.append(plot)

    plt.title("NO-NORMALIZATION")
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.legend(all_plot_, list(df[hue]), scatterpoints = 1, bbox_to_anchor = (1.05, 1), loc = 'upper left', borderaxespad = 0.)
    
    fig = plt.gcf()
    fig.set_size_inches(15, 15)
    fig.savefig(f"./output/plots/denominator={denominator}_{name}_no-normalization.png", bbox_inches = "tight", dpi = 300)
    plt.clf()


#%%
# save pca result and plots (z-score)

for k,v in zscore.items():
    name = k.split(".")[0]
    df = v.iloc[:,:].copy() # make a copy of the dataframe with PCA info (no-normalisation)
        
#     df["colour"] = df['condition'].map(populations_to_colour_mapping)
#     df["marker_plot"] = df['condition'].map(subpopulations_to_marker_mapping)

    df.to_csv(f"./output/data/denominator={denominator}_{name}_z-score.txt", sep="\t")
    
#     x_name = [col for col in list(df.columns) if col.startswith("PC_1")][0]
#     y_name = [col for col in list(df.columns) if col.startswith("PC_2")][0]
#     hue = [col for col in list(df.columns) if not col.startswith("PC_")][0]

#     all_plot_ = []
#     for j in df.index:
#         plot = plt.scatter(x = df.iloc[j][x_name], y = df.iloc[j][y_name], c = df.iloc[j]["colour"], marker = df.iloc[j]["marker_plot"], s = 200)
#         all_plot_.append(plot)

#     plt.title("Z-SCORE")
#     plt.xlabel(x_name)
#     plt.ylabel(y_name)
#     plt.legend(all_plot_, list(df[hue]), scatterpoints = 1, bbox_to_anchor = (1.05, 1), loc = 'upper left', borderaxespad = 0.)
    
#     fig = plt.gcf()
#     fig.set_size_inches(15, 15)
#     fig.savefig(f"./output/plots/denominator={denominator}_{name}_z-score.png", bbox_inches = "tight", dpi = 300)
#     plt.clf()

#%% [markdown]
# ### DREMI

#%%
df_markers = pd.read_csv(os.path.join(markers_dir, '27-markers-for-pca.txt'), sep = "\t")
markers_to_keep = list(df_markers["marker"])
markers_to_keep


#%%
# reformat the data for PCA (dremi)

d = {}

for m in markers:
    
    df_markers = pd.read_csv(os.path.join(markers_dir, m), sep = "\t")
    markers_to_keep = list(df_markers["marker"])
    
    df_one_cell_type_all_conds = pd.DataFrame()
    df_all_cell_types_all_conds = pd.DataFrame()
    
    j = 0 # counter for files (one data file per cell type)
    
    for f in files:

        df = pd.read_csv(os.path.join(files_dir, f), sep = "\t", index_col = 0)
        df = df.sort_values(by = ['file']) # check this
        print(df.shape)
        
        # make a new column for 'x_y' DREMI pairs
        for row in df.iterrows():
            df['x_y'] = df['marker_x'] + '_' + df['marker_y']  
        
        # extract and reformat dremi info
        cols_to_keep_1 = ['with_outliers_arcsinh_DREMI_score', 'x_y', 'file']
        df = df[cols_to_keep_1].iloc[:,:].copy()
        df = df.rename(columns = {'with_outliers_arcsinh_DREMI_score' : 'DREMI_score'}) 
        cols_to_keep_2 = ['x_y', 'file', 'DREMI_score']
        df = df[cols_to_keep_2].iloc[:,:]
        
        i = 0 # counter for conditions
        # extract and reformat emd info -> keep onely marker and dremi score columns
        
        conditions = list(df['file'].unique())
        for c in conditions:
            name = c.split('.')[0]
            df_1 = df[df['file'] == c].iloc[:,:].copy()
            df_1 = df_1.rename(columns = {'DREMI_score': f"{name}"}) # use condition names for dremi score column
            keep_cols = ['x_y', f"{name}"]
            df_1 = df_1[keep_cols].iloc[:,:]
            
            if i == 0:
                df_one_cell_type_all_conds = df_1.iloc[:,:].copy() # create the output dataframe for the first condition (i == 0)
            else:
                tmp = df_one_cell_type_all_conds.merge(df_1, left_on = 'x_y', right_on = 'x_y') # add a new condition to the existing dataframe (merge) (i != 0)
                df_one_cell_type_all_conds = tmp.iloc[:,:].copy()
            i += 1

        if j == 0:
            df_all_cell_types_all_conds = df_one_cell_type_all_conds.iloc[:,:].copy() # if there is only one data file (one cell type)
        else:
            tmp = df_all_cell_types_all_conds.merge(df_one_cell_type_all_conds, left_on = 'x_y', right_on = 'x_y')
            df_all_cell_types_all_conds = tmp.iloc[:,:].copy()
            
        j += 1          

    # change the index to the list of markers and transpose the dataframe
    col_to_index = ['x_y']
    df_all_cell_types_all_conds = df_all_cell_types_all_conds.set_index(col_to_index).T

    # save the result to the dictionary 'd', one key per marker list
    d[m] = df_all_cell_types_all_conds
    d[m].head()


#%%
# PCA, no-normalisation and z-score

raw = {}
zscore = {}

for k,v in d.items():
#     print(k)
    
    df = v.iloc[:,:].copy() # make a copy of the dataframe on with PCA is going to be performed
    df_standardized = pd.DataFrame(StandardScaler().fit_transform(df), columns = df.columns, index = df.index) # Standardize features by removing the mean and scaling to unit variance, i.e. z-score
    
    # PCA, no-normalisation
    pca = PCA(n_components = 2)
    principalComponents = pca.fit_transform(df)       
    explained_variance_ratio = pca.explained_variance_ratio_
    principalDf = pd.DataFrame(data = principalComponents, 
                               columns = [f"PC_1 ({explained_variance_ratio[0]*100:.2f}% explained variance)", 
                                          f"PC_2 ({explained_variance_ratio[1]*100:.2f}% explained variance)"])
    principalDf["condition"] = list(df.index)
    raw[k] = principalDf
    
    # PCA, z-score
    pca_2 = PCA(n_components = 2)
    principalComponents_2 = pca_2.fit_transform(df_standardized)       
    explained_variance_ratio_2 = pca_2.explained_variance_ratio_
    principalDf_2 = pd.DataFrame(data = principalComponents_2, 
                                 columns = [f"PC_1 ({explained_variance_ratio_2[0]*100:.2f}% explained variance)", 
                                            f"PC_2 ({explained_variance_ratio_2[1]*100:.2f}% explained variance)"])
    principalDf_2["condition"] = list(df_standardized.index)
    zscore[k] = principalDf_2   


#%%
# create a colour mapping scheme for pca plots
# or read in an existing colour mapping profile
########## unique to each experiment ##########

make_new_colour_mapping = True
colourmapping_file = "populations_to-colour-and-marker_mapping.txt"

# get the list of the conditions in the dataset
df = pd.read_csv(os.path.join(files_dir, files[0]), sep = "\t")
all_conditions = list(df["file"].unique())
all_conditions = [c.split('.')[0].lower() for c in all_conditions]
all_conditions

populations_to_colour_mapping = {}
subpopulations_to_marker_mapping = {}
    
if make_new_colour_mapping == True:
    
    # create colour palette
    unique_populations = ['stem', 'paneth', 'tuft', 'goblet', 'enteroendocrine', 'enterocyte'] # this needs a bit of design... how do you like to colour the data points on the PCA plots?
    colours_populations = sns.color_palette(n_colors = len(unique_populations)).as_hex()

    # assign colours
    for (a,b) in zip(unique_populations, colours_populations): # zip: make an iterator that aggregates elements from each of the iterables.
        for condition in all_conditions:
            if condition.startswith(a):
                populations_to_colour_mapping[condition] = b  
    
    # assign shapes/markers
    # 
    for condition in all_conditions:
        if "pRB-, CD44-" in condition:
            subpopulations_to_marker_mapping[condition] = "v"
        elif "pRB+, CD44+" in condition:
            subpopulations_to_marker_mapping[condition] = "^" 
        elif "pRB-, CD44+" in condition:
            subpopulations_to_marker_mapping[condition] = "s" 
        elif "pRB+, CD44-" in condition:
            subpopulations_to_marker_mapping[condition] = "D"  
        else:
            subpopulations_to_marker_mapping[condition] = "o"
    
    # 
    df = pd.DataFrame()
    populations = list(populations_to_colour_mapping.keys())
    colours = [populations_to_colour_mapping[x] for x in populations]
    markers = [subpopulations_to_marker_mapping[x] for x in populations]
    df["populations"] = populations
    df["colour_codes"] = colours
    df["markers"] = markers
    
    df.to_csv("populations_to-colour-and-marker_mapping.txt", sep="\t")
    
else:
    df = pd.read_csv(colourmapping_file, sep = "\t")
    for i in df.index:
        populations_to_colour_mapping[df.iloc[i]["populations"]] = df.iloc[i]["colour_codes"]
        subpopulations_to_marker_mapping[df.iloc[i]["populations"]] = df.iloc[i]["markers"]


#%%
populations_to_colour_mapping


#%%
subpopulations_to_marker_mapping


#%%
all_conditions


#%%
# save pca result and plots (no normalisation)

for k,v in raw.items():
    name = 'all-cell-type-and-subpopulations_dremi'
    df = v.iloc[:,:].copy() # make a copy of the dataframe with PCA info (no-normalisation)
    df['condition'] = df['condition'].map(str.lower) # convert conditions to lower-case
    
    df["colour"] = df['condition'].map(populations_to_colour_mapping)
    df["marker_plot"] = df['condition'].map(subpopulations_to_marker_mapping)
    
    # save coordinates
    df.to_csv(f"./output/data/{name}_no-normalization.txt", sep="\t")
    
    x_name = [col for col in list(df.columns) if col.startswith("PC_1")][0]
    y_name = [col for col in list(df.columns) if col.startswith("PC_2")][0]
    hue = [col for col in list(df.columns) if not col.startswith("PC_")][0]
    
    # save plots
    all_plot_ = []
    for j in df.index:
        plot = plt.scatter(x = df.iloc[j][x_name], y = df.iloc[j][y_name], c = df.iloc[j]["colour"], marker = df.iloc[j]["marker_plot"], s = 200)
        all_plot_.append(plot)

    plt.title("NO-NORMALIZATION")
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.legend(all_plot_, list(df[hue]), scatterpoints = 1, bbox_to_anchor = (1.05, 1), loc = 'upper left', borderaxespad = 0.)
    
    fig = plt.gcf()
    fig.set_size_inches(15, 15)
    fig.savefig(f"./output/plots/{name}_no-normalization.png", bbox_inches = "tight", dpi = 300)
    plt.clf()


#%%
# save pca result and plots (z-score)

for k,v in zscore.items():
    name = 'all-cell-type-and-subpopulations_dremi'
    df = v.iloc[:,:].copy() # make a copy of the dataframe with PCA info (no-normalisation)
    df['condition'] = df['condition'].map(str.lower) # convert conditions to lower-case
    
    df["colour"] = df['condition'].map(populations_to_colour_mapping)
    df["marker_plot"] = df['condition'].map(subpopulations_to_marker_mapping)

    df.to_csv(f"./output/data/{name}_z-score.txt", sep="\t")
    
    x_name = [col for col in list(df.columns) if col.startswith("PC_1")][0]
    y_name = [col for col in list(df.columns) if col.startswith("PC_2")][0]
    hue = [col for col in list(df.columns) if not col.startswith("PC_")][0]

    all_plot_ = []
    for j in df.index:
        plot = plt.scatter(x = df.iloc[j][x_name], y = df.iloc[j][y_name], c = df.iloc[j]["colour"], marker = df.iloc[j]["marker_plot"], s = 200)
        all_plot_.append(plot)

    plt.title("Z-SCORE")
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.legend(all_plot_, list(df[hue]), scatterpoints = 1, bbox_to_anchor = (1.05, 1), loc = 'upper left', borderaxespad = 0.)
    
    fig = plt.gcf()
    fig.set_size_inches(15, 15)
    fig.savefig(f"./output/plots/{name}_z-score.png", bbox_inches = "tight", dpi = 300)
    plt.clf()

#%% [markdown]
# ### Loop (not tested, might be easier to do 'subsetting dataframe > PCA data + plots' individually...)

#%%
dfs = {}
pcas = {}

for f in files:
    name = f.split(".txt")[0]
    df = pd.read_csv(os.path.join(files_dir, f), sep = "\t")
    
    dfs[name] = {"all": {"raw": pd.DataFrame(), "standardized": pd.DataFrame()},
                 "only_sub": {"raw": pd.DataFrame(),"standardized": pd.DataFrame()}, 
                 "only_all": {"raw": pd.DataFrame(), "standardized": pd.DataFrame()}}
    
    pcas[name] = {"all": {"raw" : pd.DataFrame(), "standardized": pd.DataFrame()},
                  "only_sub": {"raw": pd.DataFrame(), "standardized": pd.DataFrame()}, 
                  "only_all": {"raw": pd.DataFrame(), "standardized": pd.DataFrame()}}
    
    if f == "all_DREMI.txt":
        col_to_index = ["marker_x", "marker_y"]
        df = df.set_index(col_to_index).T
        names = [x.split(" DREMI_score")[0] for x in list(df.index)]
        
    if f == "all_EMD.txt":
        col_to_index = ["marker"]
        df = df.set_index(col_to_index).T
        names = [x.split(" EMD")[0] for x in list(df.index)]
        
    if f == "all_DREMI_EMD.txt":
        col_to_index = ["DREMI_marker_x", "DREMI_marker_y", "EMD_marker"]
        df = df.set_index(col_to_index).T
        names = list(df.index)
    
    only_sub = [x for x in list(df.index) if "All" not in x]
    only_all = [x for x in list(df.index) if "All" in x]
    
    df_only_sub = df.loc[only_sub, :].copy()
    df_only_all = df.loc[only_all, :].copy()
    
    df_only_sub_standardized = pd.DataFrame(StandardScaler().fit_transform(df_only_sub),columns = df_only_sub.columns, index= df_only_sub.index)
    df_only_all_standardized = pd.DataFrame(StandardScaler().fit_transform(df_only_all),columns = df_only_all.columns, index= df_only_all.index)
    df_standardized = pd.DataFrame(StandardScaler().fit_transform(df),columns = df.columns, index= df.index)
    
    ################################################################
    dfs[name]["all"]["raw"] = df
    dfs[name]["all"]["standardized"] = df_standardized
    dfs[name]["only_sub"]["raw"] = df_only_sub
    dfs[name]["only_sub"]["standardized"] = df_only_sub_standardized
    dfs[name]["only_all"]["raw"] = df_only_all
    dfs[name]["only_all"]["standardized"] = df_only_all_standardized
    ################################################################
    
    for x in ["all","only_sub","only_all"]:
        for y in ["raw", "standardized"]:
            df = dfs[name][x][y].iloc[:,:].copy()
            pca = PCA(n_components=2)
            principalComponents = pca.fit_transform(df)
            explained_variance_ratio = pca.explained_variance_ratio_
            principalDf = pd.DataFrame(data = principalComponents, 
                                       columns = [f"PC_1 ({explained_variance_ratio[0]:.2f}% explained variance)", 
                                                  f"PC_2 ({explained_variance_ratio[1]:.2f}% explained variance)"])
            principalDf["cell_type_cell_state"] = list(df.index)
            
            pcas[name][x][y] = principalDf.iloc[:,:].copy()
            
            x_name = [col for col in list(principalDf.columns) if col.startswith("PC_1")][0]
            y_name = [col for col in list(principalDf.columns) if col.startswith("PC_2")][0]
            hue = [col for col in list(principalDf.columns) if not col.startswith("PC_")][0]
            sns_plot = sns.lmplot( x = x_name, y = y_name, data = principalDf, fit_reg = False, hue = hue, legend = True)
            sns_plot.savefig(f"{pca_plots_dir}/{name}_{x}_{y}.png")

