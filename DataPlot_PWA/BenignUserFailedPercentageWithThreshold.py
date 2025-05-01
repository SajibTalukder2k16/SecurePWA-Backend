# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 20:28:16 2025

@author: sajib
"""

import pandas as pd
import matplotlib.pyplot as plt

file_path = "NormalScenario.xlsx"  
data = pd.read_excel(file_path, sheet_name=0)
df = data.iloc[2:].reset_index(drop=True)
df.columns = data.iloc[1]
df = df.apply(pd.to_numeric, errors='coerce')

user_counts = df["No of User"].unique()
thresholds = sorted(df["Threshold"].unique())

plt.figure(figsize=(10, 6))

for user_count in sorted(user_counts):
    subset = df[df["No of User"] == user_count].sort_values("Threshold")
    plt.plot(subset["Threshold"], subset["Failed Percentage"],
             marker='o', label=f"{int(user_count)} Users")

plt.xlabel("Threshold")
plt.ylabel("Failed Percentage")
plt.title("Failed Percentage vs Threshold for Different Benign User Counts")
plt.legend(title="User Count")
plt.grid(True)
plt.tight_layout()

plt.savefig("failed_percentage_benign_users.pdf")
plt.show()
plt.close()

print("Plot saved as 'failed_percentage_benign_users.pdf'")
