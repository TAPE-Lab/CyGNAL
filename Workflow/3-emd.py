###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~EMD~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# No support for IP/Jupyter notebooks or vs in files (vsNE from Cytobank)

import numpy as np
import pandas as pd
import scprep
import os
from aux3_emd_functions import *
from aux_functions import concatenate_fcs, arcsinh_transf

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PARAMETER SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
cofactor = 5
# k = 10
# n_bins = 20
# n_mesh = 3
# plot = True
# return_drevi = False
normalisation = 'no-norm'
folder_name = "input/3-emd"    # set up input directory
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#include here the information that would be helpful to understand the umaps
info_run =  input("Write EMD denominator info run (using no spaces!): ")


#~~~~~~~~~~~~~~~~~Perform transformation and concatenation~~~~~~~~~~~~~~~~~~~~#
# set up the files to be analysed (compare_from and compare_to)
# change the name of the 'compare_to‘ fcs file if needed
compare_to, input_files = concatenate_fcs(folder_name) #compare_from=inputfile
compare_to_arc, marker_list = arcsinh_transf(cofactor, compare_to)

print('Sample files:')
print('\n'.join([f for f in input_files]))
print(f'\nDenominator:\n{info_run}')
print('\nMarkers:')
print('\n'.join([m for m in marker_list]))


#Calculate EMD and save to the output folder (with denominator info run):
# calculate emd and sign the emd score by the difference of median between compare_from and compare_to

emd_df = pd.DataFrame()
emd_infodict = {}
emd_infodict["denominator"]=info_run
for compare_from_file in input_files:
    emd_infodict["file_origin"] = compare_from_file
    compare_from = pd.read_csv(f"{folder_name}/{compare_from_file}", sep = '\t')
    print (compare_from)
    compare_from_arc = arcsinh_transf(cofactor, compare_from)[0]
    #Calculate EMD for each markerVSdenominator
    emd_df = calculate_emd(marker_list, emd_infodict, compare_from_arc,
                            compare_to_arc, normalisation, emd_df)

whole_file = "EMD_" + info_run
emd_df.to_csv(f"./output/3-emd/{whole_file}.txt", index = False,
                    sep = '\t')
