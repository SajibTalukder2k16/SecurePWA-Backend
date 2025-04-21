#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 13:59:09 2025

@author: sajib
"""

import pandas as pd

# Load the CSV
df = pd.read_csv("500_10_30_input/500_10.csv")  # Replace with your file path

# Shuffle the rows randomly
df_shuffled = df.sample(frac=1).reset_index(drop=True)

# Save to a new CSV (optional)
df_shuffled.to_csv("500_10_30_input/500_10_input_random_shuffle.csv", index=False)

print("Shuffling complete. Saved as 'shuffled_file.csv'.")
