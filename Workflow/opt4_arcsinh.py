###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Arc sinh transform~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#OPTIONAL: Sometimes it might be necessary for further downstream analysis on
#other platforms to save the arsinh normalised values into the dataset.
#This script identifies the marker columns containing RAW intensities and
#overwrites them with normalised values

import os
import sys
import numpy as np
import pandas as pd
from aux_functions import *


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
folder_name = "opt4_arcsinh"

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 
    
input_dir = f"./input/{folder_name}"
output_dir = f"./output/{folder_name}"

###~Sanity check for contents~###
filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
if len(filelist) == 0:
        sys.exit(f"ERROR: There are no files in {input_dir}!")
#Check the files found in the directory:
print ("Input files:")
for i in filelist:
    print (i)

###~Co-factor~###
#Check if user wants to filter the markers based on a .csv marker file
cofactor = 5
user_cofactor = yes_or_NO(
    "Using alpha=5 for the transformation. Would you like to change this value?")
if user_cofactor:
    cofactor = int(input("Enter the new alpha to use (5=default): "))

#Load file.
    #Sanity check

#User config:
    #Alpha =5 default.
    #User given alpha
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Perform transformation~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Identify marker columns
for input_file in filelist:
    markers = []
    dataset = pd.read_csv(f"{input_dir}/{input_file}", sep = '\t')
    print("Data read!")
    markers.append([x for x in dataset.columns if x[0].isdigit()])
    print("Processed columns")
    for i in markers:
        print("Columns identified as markers: \n", i)
    print("Start transform (might take around 10min with larger datasets)")
    normalised_dataset = arcsinh_transf(cofactor, dataset)[0]
    print("Finished transform")
    print("Start writing results to file (might take some time with larger datasets)")
    normalised_dataset.to_csv(f"{output_dir}/arcsinhTRANSF_{input_file}", index=False, sep = '\t')

#Function:
    #id MARKERS 
        #Report which markers were Ided
    #Transform and overwrite the values
    #Return dataset

#Write resulting file