#! python3
import os
import pandas as pd
import sys

filelist = [f for f in os.listdir(f"./input/opt3_reindex") if f.endswith(".csv") or f.endswith(".txt")]

folder_name = 'opt3_reindex'

if os.path.isdir(f"./output/{folder_name}") == False:
    os.makedirs(f"./output/{folder_name}")
if os.path.isdir(f"./input/{folder_name}") == False:
    os.makedirs(f"./input/{folder_name}")
    sys.exit("ERROR: There is no input folder") 

for f in filelist:
    df = pd.read_csv(f'./input/opt3_reindex/{f}', sep = '\t', index_col = 0)
    df.index = pd.RangeIndex(len(df.index))
    df['new-cell-index'] = df.index + 1
    df.to_csv(f'./output/opt3_reindex/{f}', sep = '\t', index = False)


