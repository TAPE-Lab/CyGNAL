###############################################################################
#~~~~~~~~~~~~~~~~~~~#~Convert txt to fcs and viceversa~#~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
#OPTIONAL: Sometimes the user may want to save concatenated sample files for 
#downstream analysis, e.g. concatenate technical replicates


import os  # Fix importing from diff. directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import re
import pandas as pd
import fcswrite
import fcsparser
from sklearn.preprocessing import OrdinalEncoder
from aux.aux_functions import *


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
input_dir = f"{base_dir}/Utils_Data/input/opt5_conversion"
output_dir = f"{base_dir}/Utils_Data/output/opt5_conversion"

txt_filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
fcs_filelist = [f for f in os.listdir(input_dir) if f.endswith(".fcs")]
filelist = txt_filelist+fcs_filelist

if len(filelist)==0:
    sys.exit (f"ERROR: There are no files in {input_dir}!")
if len(txt_filelist)!=0:
    print("Found the following .txt files: ", txt_filelist)
if len(fcs_filelist)!=0:
    print("Found the following .fcs files: ", fcs_filelist)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

for i in filelist:
    file_path = f"{input_dir}/{i}"
    name = i.split('.')[0]
    if i in txt_filelist:
        print("\n",i)
        df = pd.read_csv(file_path, sep = '\t')
        if len(df.select_dtypes(exclude="number").columns) !=0:
            print("Found some columns in the .txt file containing non-numeric values")
            if "file_identifier" in df.select_dtypes(exclude="number").columns:
                print("Identified columns with file of origin information from past concatenation step.",
                "Re-encoding them as numerical values. Check ouput for equivalence table")
                df["file_number"] = OrdinalEncoder().fit_transform(df[["file_origin"]])
                object_test = df.groupby(["file_number","file_origin"]).groups.keys()
                equivalence_table = pd.DataFrame(list(object_test),
                                        columns=["file_number","file_origin"])
                print("Saving equivalence table:\n", equivalence_table)
                equivalence_table.to_csv(f"{output_dir}/CONVtxt2fcs_{i.split('.txt')[0]}_EquivalenceTable.csv", 
                                        index=False)
            print("The following columns with non-numerical values will be removed:")
            print(df.select_dtypes(exclude="number").columns)
            df = df.select_dtypes(include="number")
        print(f"Saving {i} as FCS...")
        print(df.head())
        fcswrite.write_fcs(f"{output_dir}/CONVtxt2fcs_{i.split('.txt')[0]}.fcs", 
                            chn_names=list(df.columns),
                            compat_chn_names=False, 
                            data=df.to_numpy())
    else: #file is an FCS
        try: #Use fcsparser to read the fcs data files
            print("\n",i)
            df = fcsparser.parse(file_path, meta_data_only=False)[1]
            reg_pnn = re.compile("(\d+Di$)") #Detect if, despite flag
            pnn_extracted=[]                 #columns match PnN pattern
            for n in df.columns.values.tolist():
                if reg_pnn.search(n):
                    pnn_extracted.append(n)
            if len(pnn_extracted)!=0:
                raise fcsparser.api.ParserFeatureNotImplementedError
        except fcsparser.api.ParserFeatureNotImplementedError:
            print("WARNING: Non-standard .fcs file detected: ", i)
            #use rpy2 to read the files and load into python
            df = read_rFCS(file_path)[0]
        print(f"Saving {i} as .txt...")
        print(df.head())
        df.to_csv(f"{output_dir}/CONVfcs2txt_{i.split('.fcs')[0]}.txt")


