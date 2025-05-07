#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 02:18:41 2024

@author: yueyuemin
"""

import pandas as pd
from pathlib import Path
base_dir = Path("/Users/yueyuemin/Documents/school/QMSS/Thesis/data/raw")
file_name = ["nyt_articles_2005_2015.csv",
             "nyt_articles_1994_2004.csv",
             "nyt_articles_2016_2017.csv",
             "nyt_articles_2018_2024.csv"
             ]
data_path = [base_dir / fn for fn in file_name]

dfs = (pd.read_csv(file, chunksize=10_000) for file in data_path)  # Read in chunks
merged_df = pd.concat(chunk for df in dfs for chunk in df)

# Save the merged result
output_path = base_dir / "merged_nyt_articles_1994_2024.csv"
merged_df.to_csv(output_path, index=False)

print(f"Merged data saved to {output_path}")