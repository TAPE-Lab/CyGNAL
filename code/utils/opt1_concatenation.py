###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~#~Concatenate and Save~#~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#OPTIONAL: Sometimes the user may want to save concatenated sample files for 
#downstream analysis, e.g. concatenate technical replicates
#Jupyter/IP no longer supported here

import os, sys #Fix importing from diff. directory
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

filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
if len(filelist) == 0:
    sys.exit(f"ERROR: There are no .txt files in {input_dir}!")
#Check the files found in the directory:
print ("Concatenate script supports only .txt files. Input files:")
for i in filelist:
    print (i)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

concatenate_save(input_dir, output_dir)
