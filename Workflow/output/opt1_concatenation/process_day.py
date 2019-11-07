import pandas as pd
import sys
import os
import re


if os.path.isdir(f"./Processed") == False:
    os.makedirs(f"./Processed")

filelist = [f for f in os.listdir() if f.endswith(".txt")]
print ("Input files:")

reg_filter = re.compile("-(\d)_")
for i in filelist:
    print (i)
    df = pd.read_csv(f"./{i}", sep = '\t')
    df["Day"] = df["file_origin"].apply(
                                        lambda x: reg_filter.search(x).group(1)) #File+ID #This way the cell-index will be preserved after Cytobank upload
        # df["Cell_Index"] = df["Cell_Index"].apply(lambda x: str(fcounter)+"-"+str(x)) #File+ID
    processed = df.drop(columns=["file_origin","Sample_ID-Cell_Index"])
    processed.to_csv(f"./Processed/processed_day.txt", index = False, sep = '\t')
