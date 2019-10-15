# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%% Change working directory from the workspace root to the ipynb file location.
# Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(),
        '../../../../../../var/folders/95/kmz2y98s2pn02b7lmnk8blsr0000gn/T'))
	print(os.getcwd())
except:
	pass

#%%
import os, glob
import pandas as pd
import numpy as np
import holoviews as hv
import re
from IPython.core.interactiveshell import InteractiveShell


#%%
# wide cells
hv.extension("bokeh", width=90)
# display all output in each cell
InteractiveShell.ast_node_interactivity = "all"


#%%
# prepare file list; put the data files to be processed in the 'input' folder
# most of the time these files should share the same panel
# put the files in a list (txt/csv)
filelist = [f for f in os.listdir(f"./input") if f.endswith(".txt")]
# filelist = [f for f in os.listdir(f"./input") if f.endswith(".csv")]
filelist

#Check the files found in the directory:
for i in filelist:
    print (i)
#%% [markdown]
#FUTURE WORK: Once I have gone through all steps, implement the code as 
# functions and write and overarching script to run everything as a 
# consolidated pipeline -> Might have to split it whenever Cytobank is involved 
#%%
# get the original column names
file = f"./input/{filelist[0]}"
df_file = pd.read_csv(file, sep = '\t')
type(df_file)
df_file
df_file_cols = list(df_file.columns)

df_file_cols

#%%
#FCR 14/10/19: Automated column name editing with regex
#Idea is to rename all columns and then filter non-relevant ones (less optimal,
# easier and more compatible with writing new reduced file in the last step)

#Renaming
def rename_columns(df_file_cols):
    reg_rename = re.compile("(__[a-z].*$|__\d.*$|_\(.*$|___.*$)")
    df_file_cols_processed = []
    df_file_cols_renamed = []
    for i in df_file_cols:
        try:
            df_file_cols_processed.append(reg_rename.sub("",i))
        except:
            df_file_cols_processed.append(i)
    #Second pass to remove trailing underscores
    for i in df_file_cols_processed:
        try:
            df_file_cols_renamed.append(re.sub(r"_$","",i))
        except:
            df_file_cols_renamed.append(i)
    # Keeping with Xiao's convention, rename Event # to Cell_Index
    for n,i in enumerate(df_file_cols_renamed):
        if i=="Event #":
            df_file_cols_renamed[n] = "Cell_Index"
    
    return df_file_cols_renamed

renamed_columns = rename_columns(df_file_cols)

# len(renamed_columns)
# len(df_file_cols)
# renamed_columns
df_file_cols

#%%
#Filtering
def filter_columns(renamed_columns):
    reg_filter = re.compile("^\d+[A-Za-z]+$")
    filtered_columns = [] #Stores the columns that where deemed unnecessary
    columns_to_keep = [] #Columns that the reduced file should have
    for i in renamed_columns:
        if reg_filter.search(i):
            filtered_columns.append(i)
        else:
            columns_to_keep.append(i)
    return columns_to_keep, filtered_columns

columns_to_keep, filtered_columns = filter_columns(renamed_columns)

# for i in filtered_columns:
#     print (i)
# len(filtered_columns)
# len(renamed_columns)

#%%
# Final step: Write reduced file
for file in filelist:
    name = file.split(".")[0] # change this line based on the naming of the input files
    
    f = pd.read_csv(os.path.join(f"./input/{file}"), sep="\t")
    
    file_cols = list(f.columns)
    if file_cols == df_file_cols: # again, all the files should share the same panel
        f.columns = renamed_columns
        f_reduced = f[columns_to_keep].iloc[:].copy()
        f_reduced.to_csv(f"./output/{name}.txt", index = False, sep = '\t') 
            # index = False to be compatible with Cytobank
        
        # print the info of the renaming procedure
        shape_before = f.shape
        shape_after = f_reduced.shape
        print(f"file: {name}\nrows before: {shape_before[0]} - columns before: {shape_before[1]}\nrows after: {shape_after[0]} - columns after: {shape_after[1]}\n")

    else:
        print(f"{file} HAS NOT THE SAME COLUMNS")

#%%
# DEPRECATED old info (51<53 since we now keep Cisplatin and Event#/Cell_Index)
# file: figure-1_full-gate_1st-cytobank-export_no-arcsinh
# rows before: 1002294 - columns before: 76
# rows after: 1002294 - columns after: 51

#DEPRECATED
# # first copy the column names
# # rename the columns in place, don't delete any item from the list now
# renamed_panel = ['Event #',
#  'Time',
#  'Event Length',
#  '75As_(As75Di)',
#  '89Y_pHH3',
#  '111Cd_(Cd111Di)',
#  '112Cd_(Cd112Di)',
#  '113In_EpCAM',
#  '114Cd_(Cd114Di)',
#  '115In_Pan-CK',
#  '116Cd_(Cd116Di)',
#  '117Sn_(Sn117Di)',
#  '120Sn_(Sn120Di)',
#  '124Te_(Te124Di)',
#  '126Te_(Te126Di)',
#  '127I_IdU',
#  '128Te_(Te128Di)',
#  '130Te_TePhe',
#  '131Xe_(Xe131Di)',
#  '133Cs_(Cs133Di)',
#  '137Ba_(Ba137Di)',
#  '138Ba_(Ba138Di)',
#  '139La_(La139Di)',
#  '140Ce_EQ Beads',
#  '141Pr_pPDPK1',
#  '142Nd_cCaspase 3',
#  '143Nd_C-MYC',
#  '144Nd_Lysozyme',
#  '145Nd_FABP1',
#  '146Nd_pMKK4_SEK1',
#  '147Sm_pBTK',
#  '148Nd_pSRC',
#  '149Sm_p4E-BP1',
#  '150Nd_pRB',
#  '151Eu_pPKCa',
#  '152Sm_pAKT T308',
#  '153Eu_pCREB',
#  '154Sm_pSMAD1_5_9',
#  '155Gd_pAKT S473',
#  '156Gd_pNF-kB p65',
#  '157Gd_pMKK3_MKK6',
#  '158Gd_pP38 MAPK',
#  '159Tb_pMAPKAPK2',
#  '160Gd_pAMPKa',
#  '161Dy_pBAD',
#  '162Dy_LRIG1',
#  '163Dy_pP90RSK',
#  '164Dy_pP120-Catenin',
#  '165Ho_Beta-Catenin_Active',
#  '166Er_pGSK3b',
#  '167Er_pERK1_2',
#  '168Er_pSMAD2_3',
#  '169Tm_GFP',
#  '170Er_pMEK1_2',
#  '171Yb_CLCA1',
#  '172Yb_pS6',
#  '173Yb_DCAMKL1',
#  '174Yb_CHGA',
#  '175Lu_CD44',
#  '176Yb_Cyclin B1',
#  '176Lu_(Lu176Di)',
#  '190Pt_(Pt190Di)',
#  '191Ir_DNA 1',
#  '192Pt_(Pt192Di)',
#  '193Ir_DNA 2',
#  '194Pt_(Pt194Di)',
#  '195Pt_(Pt195Di)',
#  '196Pt_(Pt196Di)',
#  '198Pt_Cisplatin',
#  '199Hg_(Hg199Di)',
#  '200Hg_(Hg200Di)',
#  '209Bi_DiMeHH3',
#  'Center',
#  'Offset',
#  'Width',
#  'Residual']

# cols_to_keep = ['Time',
#  'Event Length',
#  '89Y_pHH3',
#  '113In_EpCAM',
#  '115In_Pan-CK',
#  '127I_IdU',
#  '130Te_TePhe',
#  '140Ce_EQ Beads',
#  '141Pr_pPDPK1',
#  '142Nd_cCaspase 3',
#  '143Nd_C-MYC',
#  '144Nd_Lysozyme',
#  '145Nd_FABP1',
#  '146Nd_pMKK4_SEK1',
#  '147Sm_pBTK',
#  '148Nd_pSRC',
#  '149Sm_p4E-BP1',
#  '150Nd_pRB',
#  '151Eu_pPKCa',
#  '152Sm_pAKT T308',
#  '153Eu_pCREB',
#  '154Sm_pSMAD1_5_9',
#  '155Gd_pAKT S473',
#  '156Gd_pNF-kB p65',
#  '157Gd_pMKK3_MKK6',
#  '158Gd_pP38 MAPK',
#  '159Tb_pMAPKAPK2',
#  '160Gd_pAMPKa',
#  '161Dy_pBAD',
#  '162Dy_LRIG1',
#  '163Dy_pP90RSK',
#  '164Dy_pP120-Catenin',
#  '165Ho_Beta-Catenin_Active',
#  '166Er_pGSK3b',
#  '167Er_pERK1_2',
#  '168Er_pSMAD2_3',
#  '169Tm_GFP',
#  '170Er_pMEK1_2',
#  '171Yb_CLCA1',
#  '172Yb_pS6',
#  '173Yb_DCAMKL1',
#  '174Yb_CHGA',
#  '175Lu_CD44',
#  '176Yb_Cyclin B1',
#  '191Ir_DNA 1',
#  '193Ir_DNA 2',
#  '209Bi_DiMeHH3',
#  'Center',
#  'Offset',
#  'Width',
#  'Residual']

#DEPRECATED @Ferran
#DEPRECATED->FC
# #FCR 14/10/19: Automated column name editing with regex --TESTING GROUNDS--
# import re

# #Idea is to first filter non-relevant columns and then rename the remaining
# reg_filter = re.compile("^\d*[A-Za-z]*_\(.*$")
# reg_rename = re.compile("(__[a-z].*$|__\d.*$|_\(.*$|___.*$)")

# #Filtering
# df_file_cols_testing = []
# df_file_cols_filtered = []

# len(df_file_cols)
                        
# for i in df_file_cols:
#     if reg_filter.search(i):
#         df_file_cols_filtered.append(i)
#     else:
#         df_file_cols_testing.append(i)    
# len(df_file_cols_testing)
# for i in df_file_cols_filtered:
#     print (i)
# len(df_file_cols_filtered)

# # Keeping with Xiao's convention, rename Event # to Cell_Index
# for n,i in enumerate(df_file_cols_testing):
#     if i=="Event #":
#         df_file_cols_testing[n] = "Cell_Index"

# for i in df_file_cols_testing:
#     print(i)

# #Start with the renaming!

# df_file_cols_processed = []

# for i in df_file_cols_testing:
#     try:
#         df_file_cols_processed.append(reg_rename.sub("",i))
#     except:
#         df_file_cols_processed.append(i)

# #Second pass to remove trailing underscores
# df_file_cols_final =[]
# for i in df_file_cols_processed:
#     try:
#         df_file_cols_final.append(re.sub(r"_$","",i))
#     except:
#         df_file_cols_final.append(i)


# len(df_file_cols_processed)
# for i in df_file_cols_processed:
#     print (i)
# len(df_file_cols_final)
# for i in df_file_cols_final:
#     print (i)
# #TEST V0: __([a-z].*$|)
