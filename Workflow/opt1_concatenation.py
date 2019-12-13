###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~#~Conncatenate and Save~#~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#OPTIONAL: Sometimes the user may want to save concatenated sample files for 
#downstream analysis, e.g. concatenate technical replicates
#Jupyter/IP no longer supported here

import pandas as pd
from aux_functions import *

# prepare file list
# The user needs to manually move the files to be concatenated (possibly in batches) to the 'opt1_concatenation' folder
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME PANEL
# The concatenated file will be saved in the 'output/opt1_concatenation' folder
# The user will need to change the name of the concatenate file and move it to the input folder for the next step

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~CONFIG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "opt1_concatenation"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 
    
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
#Check the files found in the directory:
print ("Input files:")
for i in filelist:
    print (i)

concatenate_save(input_dir, output_dir)