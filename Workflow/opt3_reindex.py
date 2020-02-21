#! python3
import os
import pandas as pd

filelist = [f for f in os.listdir(f"./input/opt3_reindex") if f.endswith(".csv") or f.endswith(".txt")]

for f in filelist:
    df = pd.read_csv(f'./input/opt3_reindex/{f}', sep = '\t', index_col = 0)
    df.index = pd.RangeIndex(len(df.index))
    df['new-cell-index'] = df.index + 1
    df.to_csv(f'./output/opt3_reindex/{f}', sep = '\t', index = False)


