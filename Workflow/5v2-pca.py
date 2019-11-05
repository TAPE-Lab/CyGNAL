
import subprocess
import os
import sys
from aux_functions import yes_or_NO
#Import yes or no question to choose the different plotings
#Run the separate R shiny apps accordingly
#2 options for the PCA plots:
    #Either run basic PCA on R and plot in shiny app (less graphical customisation, simpler plots)
    #Leverage PCA shiny apps. 
        #PCAshiny from Factoshiny -> Very basic
        #Interactive PCA Explorer


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
emd = yes_or_NO("Perform PCA on the EMD scores?")
dremi = yes_or_NO("Perform PCA on the DREMI scores?")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Input files should have either emd or dremi on their name

if emd==True and dremi==False:
    emd_file = []
    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            if "emd" in file.lower():
                emd_file.append(file)
    if len(emd_file) != 1:
            sys.exit("ERROR: Please have only ONE .txt file with 'emd' in its name!")
    emd_file = f"{input_dir}/{emd_file[0]}"
    subprocess.call(["bash","5v2_pca_emd.sh", emd_file])

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
    subprocess.call(["bash","5v2_pca_both.sh", emd_file, dremi_file])

if emd==False and dremi==True:
    dremi_file = []
    for file in os.listdir(input_dir):
        if file.endswith(".txt"):
            if "dremi" in file.lower():
                dremi_file.append(file)
    if len(dremi_file) != 1:
        sys.exit("ERROR: Please have only ONE .txt file with 'dremi' in its name!")
    dremi_file = f"{input_dir}/{dremi_file[0]}"
    subprocess.call(["bash","5v2_pca_dremi.sh", dremi_file])

if emd==False and dremi==False:
    sys.exit("THEN THERE'S NOTHING TO DO!")
