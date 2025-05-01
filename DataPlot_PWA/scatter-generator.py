# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 12:39:38 2025

@author: sajib
"""
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

df = pd.read_excel("MaliciousScenario.xlsx", skiprows=2)
df.columns = ['No of User', 'Attack Devices', 'Threshold', 'Total Requests',
              'Successful Requests', 'Failed Requests', 'Failed Percentage']
df = df.apply(pd.to_numeric, errors='coerce').dropna()

X = df['No of User']
Y = df['Attack Devices']
Z = df['Threshold']
C = df['Failed Percentage']

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(X, Y, Z, c=C, cmap=cm.viridis, s=70)
ax.set_xlabel('No of User')
ax.set_ylabel('Attack Devices')
ax.set_zlabel('Threshold')
ax.set_title('3D Scatter: Failed Percentage')

# Add color bar
fig.colorbar(sc, ax=ax, label='Failed Percentage')

plt.tight_layout()
plt.savefig("3D_Scatter_Failed_Percentage.pdf")
plt.show()
