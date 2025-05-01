# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 12:29:12 2025

@author: sajib
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_excel("MaliciousScenario.xlsx", skiprows=2)
df.columns = ['No of User', 'Attack Devices', 'Threshold', 'Total Requests',
              'Successful Requests', 'Failed Requests', 'Failed Percentage']
df = df.apply(pd.to_numeric, errors='coerce').dropna()

def generate_and_show_heatmap(index_var, column_var, filename):
    pivot = df.pivot_table(index=index_var, columns=column_var, values='Failed Percentage', aggfunc='mean')

    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=0.5)
    plt.title(f"Failed Percentage Heatmap ({index_var} vs {column_var})")
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()

generate_and_show_heatmap('No of User', 'Threshold', 'heatmap_users_vs_threshold.pdf')
generate_and_show_heatmap('No of User', 'Attack Devices', 'heatmap_users_vs_devices.pdf')
generate_and_show_heatmap('Threshold', 'Attack Devices', 'heatmap_threshold_vs_devices.pdf')
