#! python3
###########################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Integration~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###########################################################################

#### Note: This script takes the outputs of 6-cell_state_info.py and 
# 7-cell_type_info.py as inputs. The output file will be the original
# CyTOF data joined by two columns of cell-state info (cell_state and cell_
# state_num), together with 6 columns of the six cell-type markers.

# setup the environment
import sys
import os
import copy
import pandas as pd
import numpy as np
from aux_functions import yes_or_NO

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Sanity Check~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# file_name_format = yes_or_NO("Are all the files named in the 'sample-name_cell-type' format?")
# if file_name_format == False:
#     sys.exit(f"Please rename the files to the 'sample_cell-type' format\n Accepted cell-types (literal): stem, paneth, enteroendocrine, tuft, goblet, and enterocyte") 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "8-cell_type-state_integration"
if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    # sys.exit("ERROR: There is no input folder") 

# prepare files
cell_state_file = [f for f in os.listdir(f"./input/{folder_name}") if 'cell-state' in f]
cell_type_file = [f for f in os.listdir(f"./input/{folder_name}") if 'cell-type' in f]

sample = cell_state_file[0].split('_')[0]

df_state = pd.read_csv(f'./input/{folder_name}/{cell_state_file[0]}', sep = '\t')
df_type = pd.read_csv(f'./input/{folder_name}/{cell_type_file[0]}', sep = '\t')

df = df_state.join(df_type.set_index('Cell_Index'), on='Cell_Index')
df.to_csv(f'./output/{folder_name}/{sample}_w-cell-state_w-cell-type.txt', index = False, sep = '\t')
print(f"Output file(s) saved in the folder './output/{folder_name}'")