import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

df = pd.read_excel("MaliciousScenario.xlsx", skiprows=2)
df.columns = ['No of User', 'Attack Devices', 'Threshold', 'Total Requests',
              'Successful Requests', 'Failed Requests', 'Failed Percentage']
df = df.apply(pd.to_numeric, errors='coerce').dropna()

fixed_variable = 'Threshold'  # Change to: 'No of User', 'Attack Devices', or 'Threshold'
fixed_value = 30              # Change value depending on fixed_variable

if fixed_variable == 'Threshold':
    x_var, y_var = 'No of User', 'Attack Devices'
elif fixed_variable == 'No of User':
    x_var, y_var = 'Threshold', 'Attack Devices'
elif fixed_variable == 'Attack Devices':
    x_var, y_var = 'No of User', 'Threshold'
else:
    raise ValueError("Invalid fixed_variable")

df_plot = df[df[fixed_variable] == fixed_value]

x = np.linspace(df_plot[x_var].min(), df_plot[x_var].max(), 20)
y = np.linspace(df_plot[y_var].min(), df_plot[y_var].max(), 20)
X, Y = np.meshgrid(x, y)

points = df_plot[[x_var, y_var]].values
values = df_plot['Failed Percentage'].values
Z = griddata(points, values, (X, Y), method='linear')

# Plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, edgecolor='none', alpha=0.9)

ax.set_xlabel(x_var)
ax.set_ylabel(y_var)
ax.set_zlabel('Failed Percentage')
ax.set_title(f'3D Surface Plot ({fixed_variable} = {fixed_value})')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

fig.savefig("3D_Surface_Failed_Percentage.pdf", format='pdf')
print("Plot saved as 3D_Surface_Failed_Percentage.pdf")
