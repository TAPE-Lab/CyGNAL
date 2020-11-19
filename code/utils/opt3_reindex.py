#! python3
import os, sys #Fix importing from diff. directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import pandas as pd

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~I/O~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
input_dir = f"{base_dir}/Utils_Data/input/opt3_reindex"
output_dir = f"{base_dir}/Utils_Data/output/opt3_reindex"

filelist = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
if len(filelist) == 0:
    sys.exit(f"ERROR: There are no .txt files in {input_dir}!")
#Check the files found in the directory:
print ("Reindex script supports only .txt files. Input files:")
for i in filelist:
    print (i)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

for f in filelist:
    df = pd.read_csv(f"{input_dir}/{f}", sep = '\t', index_col = 0)
    df.index = pd.RangeIndex(len(df.index))
    df['new-cell-index'] = df.index + 1
    df.to_csv(f"{output_dir}/{f}", sep = '\t', index = False)

print(f"Reindexed files saved in {output_dir}")


