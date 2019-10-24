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
# IF WORKING WITH MULTIPLE FILES THEY SHOULD SHARE THE SAME MARKER
# The concatenated file will be saved in the 'output/opt1_concatenation' folder
# The user will need to change the name of the concatenate file and move it to the input folder for the next step
folder_name = "./input/opt1_concatenation"
filelist = [f for f in os.listdir(f"{folder_name}") if f.endswith(".txt")]

#Check the files found in the directory:
print ("Input files:")
for i in filelist:
    print (i)

concatenate_save(folder_name)