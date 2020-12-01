###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Heatmaps~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#Plot EMD and DREMI scores as heatmaps
import os
import subprocess
import sys

from aux.aux_functions import yes_or_NO

#Import yes or no question to choose the different plotings
#Run the separate R shiny apps accordingly
#Simultaneous emd and DREMI should both be possible since the ports are random


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
aux_dir = os.path.dirname(os.path.abspath(__file__))+"/aux"

input_dir = f"{base_dir}/Analysis/Vis_Heatmap"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~User Input~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
emd = yes_or_NO("Plot EMD scores on a heatmap?", default="YES")
dremi = yes_or_NO("Plot DREMI scores on a heatmap?")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Execute shiny Apps~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Input files should have either emd or dremi on their name. 
if emd==True and dremi==False:
    emd_file = []
    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            if "emd" in file.lower():
                emd_file.append(file)
    if len(emd_file) != 1:
            sys.exit("ERROR: Please have only ONE .txt file with 'emd' in its name!")
    emd_file = f"{input_dir}/{emd_file[0]}"
    subprocess.call(["bash",f"{aux_dir}/aux5v1_emd.sh", emd_file], cwd=aux_dir)
                                                            #cwd to point to aux
if emd==True and dremi==True:
    emd_file = []
    dremi_file = []
    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            if "emd" in file.lower():
                emd_file.append(file)
            elif "dremi" in file.lower():
                dremi_file.append(file)
    if len(emd_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'emd' in its name!")
    if len(dremi_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'dremi' in its name!")
    emd_file = f"{input_dir}/{emd_file[0]}"
    dremi_file = f"{input_dir}/{dremi_file[0]}"
    subprocess.call(["bash",f"{aux_dir}/aux5v1_both.sh", emd_file, 
                        dremi_file], cwd=aux_dir)

if emd==False and dremi==True:
    dremi_file = []
    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            if "dremi" in file.lower():
                dremi_file.append(file)
    if len(dremi_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'dremi' in its name!")
    dremi_file = f"{input_dir}/{dremi_file[0]}"
    subprocess.call(["bash",f"{aux_dir}/aux5v1_dremi.sh", dremi_file], 
                    cwd=aux_dir)

if emd==False and dremi==False:
    sys.exit("THEN THERE'S NOTHING TO DO!")

