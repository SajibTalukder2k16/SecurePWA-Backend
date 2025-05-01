# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 13:21:33 2025

@author: sajib
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

malicious_df = pd.read_excel("MaliciousScenario.xlsx", skiprows=2)
normal_df = pd.read_excel("NormalScenario.xlsx", skiprows=2)

columns = ['No of User', 'Attack Devices', 'Threshold', 'Total Requests',
           'Successful Requests', 'Failed Requests', 'Failed Percentage']
malicious_df.columns = columns
normal_df.columns = columns

# === Clean Data ===
malicious_df = malicious_df.apply(pd.to_numeric, errors='coerce').dropna()
normal_df = normal_df.apply(pd.to_numeric, errors='coerce').dropna()

# === Label Scenarios and Merge ===
malicious_df['Scenario'] = 'Malicious'
normal_df['Scenario'] = 'Normal'
combined_df = pd.concat([malicious_df, normal_df], ignore_index=True)

# === 1. Bar Plot by Threshold ===
plt.figure(figsize=(12, 6))
sns.barplot(data=combined_df, x='Threshold', y='Failed Percentage', hue='Scenario', ci=None)
plt.title('Failed Percentage Comparison by Threshold')
plt.ylabel('Failed Percentage')
plt.tight_layout()
plt.savefig("bar_threshold_comparison.pdf")
plt.show()

# === 2. Bar Plot by No of User ===
plt.figure(figsize=(12, 6))
sns.barplot(data=combined_df, x='No of User', y='Failed Percentage', hue='Scenario', ci=None)
plt.title('Failed Percentage Comparison by No of User')
plt.ylabel('Failed Percentage')
plt.tight_layout()
plt.savefig("bar_user_comparison.pdf")
plt.show()

# === 3. Line Plot by Users, grouped by Threshold ===
plt.figure(figsize=(12, 6))
sns.lineplot(data=combined_df, x='No of User', y='Failed Percentage', hue='Scenario',
             style='Threshold', markers=True, dashes=False)
plt.title('Failed Percentage vs No of User (Grouped by Threshold)')
plt.tight_layout()
plt.savefig("line_users_threshold_comparison.pdf")
plt.show()

# === 4. Line Plot by Threshold, grouped by Attack Devices ===
plt.figure(figsize=(12, 6))
sns.lineplot(data=combined_df, x='Threshold', y='Failed Percentage', hue='Scenario',
             style='Attack Devices', markers=True, dashes=False)
plt.title('Failed Percentage vs Threshold (Grouped by Attack Devices)')
plt.tight_layout()
plt.savefig("line_threshold_devices_comparison.pdf")
plt.show()

# === 5. 3D Scatter Plot ===
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
colors = {'Malicious': 'red', 'Normal': 'green'}

for scenario in combined_df['Scenario'].unique():
    subset = combined_df[combined_df['Scenario'] == scenario]
    ax.scatter(subset['No of User'], subset['Attack Devices'], subset['Threshold'],
               c=colors[scenario], label=scenario, s=60, alpha=0.7)

ax.set_xlabel('No of User')
ax.set_ylabel('Attack Devices')
ax.set_zlabel('Threshold')
ax.set_title('3D Scatter Plot: Malicious vs Normal Scenarios')
ax.legend()
plt.tight_layout()
plt.savefig("3D_scatter_malicious_vs_normal.pdf")
plt.show()
