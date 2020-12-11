###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~#~Concatenate and Save~#~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#OPTIONAL: Sometimes the user may want to save concatenated sample files for 
#downstream analysis, e.g. concatenate technical replicates. 
# Takes in both .txt files and FCS files but outputs only .txt files

import os  # Fix importing from diff. directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import pandas as pd
from aux.aux_functions import *

# prepare file list
# The user needs to manually move the files to be concatenated (possibly in batches) to the 'opt1_concatenation' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME PANEL
# The concatenated file will be saved in the 'output/opt1_concatenation' folder
# The user will need to change the name of the concatenate file and move it to the input folder for the next step

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
input_dir = f"{base_dir}/Utils_Data/input/opt1_concatenation"
output_dir = f"{base_dir}/Utils_Data/output/opt1_concatenation"

info_run =  input("Write info run (using no spaces!): ")
if len(info_run) == 0:
    print("No info run given. Saving results in UNNAMED")
    info_run = "UNNAMED"

if os.path.isdir(f"{output_dir}/{info_run}") == False:
    os.makedirs(f"{output_dir}/{info_run}")
else:
    if info_run !="UNNAMED":
        sys.exit("ERROR: You already used this name for a previous run. \nUse a different name!")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# concatenate_save(input_dir, output_dir)

concat_df, filelist = concatenate_fcs(input_dir)

concat_df.to_csv(f"{output_dir}/{info_run}/CONCAT_{info_run}.txt", index = False, sep = '\t')

# import fcswrite
# fcs_sopts = yes_or_NO("Saving CONCAT as .txt. Would you like to try and save the concatenated dataset as a .fcs ?")
# if fcs_sopts:
#     try:
#         print(type(list(concat_df.columns)), list(concat_df.columns))
#         print(type(concat_df.to_numpy()), concat_df.to_numpy())
#         fcswrite.write_fcs(f"{output_dir}/{info_run}/CONCAT_{info_run}.fcs", 
#                             chn_names=list(concat_df.columns),
#                             compat_chn_names=False, data=concat_df.to_numpy())
#     except TypeError:
#         print("ERROR when saving as FCS. Dropping non numerical columns")
#         concat_df.drop(["file_origin","file_identifier","Sample_ID-Cell_Index"],axis=1, inplace=True)
#         concat_df.to_csv(f"{output_dir}/{info_run}/CONCAT_{info_run}.txt", index = False, sep = '\t')
#         print(type(list(concat_df.columns)), list(concat_df.columns))
#         print(type(concat_df.to_numpy()), concat_df.to_numpy())

