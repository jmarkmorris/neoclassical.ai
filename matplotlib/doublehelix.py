# python doublehelix.py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create a new figure
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Parameters for the cylinder
length = 40  # Length of the cylinder
radius = 2   # Radius of the cylinder

# Create the cylinder coordinates (horizontal pipe)
theta = np.linspace(0, 2 * np.pi, 100)
x = np.linspace(0, length, 100)  # Along x-axis
theta, x = np.meshgrid(theta, x)
y = radius * np.cos(theta)
z = radius * np.sin(theta)

# Plot the cylinder surface with reduced shading
ax.plot_surface(x, y, z, color='lightblue', alpha=0.3)  # Reduced alpha for less shading

# Create a double helix along the length of the cylinder
t = np.linspace(0, length, 1000)
cycles = 2
x_helix = t
y_helix1 = radius * np.cos(2 * np.pi * t / length * cycles)
z_helix1 = radius * np.sin(2 * np.pi * t / length * cycles)
y_helix2 = radius * np.cos(2 * np.pi * t / length * cycles + np.pi)
z_helix2 = radius * np.sin(2 * np.pi * t / length * cycles + np.pi)

# Plot the double helix
ax.plot(x_helix, y_helix1, z_helix1, color='red')
ax.plot(x_helix, y_helix2, z_helix2, color='blue')

# Remove grid and set labels
ax.grid(False)

# Remove numbers from axes but keep tick marks
ax.xaxis.set_tick_params(labelsize=0)
ax.yaxis.set_tick_params(labelsize=0)
ax.zaxis.set_tick_params(labelsize=0)

# Hide axis labels
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])

# Set aspect ratio to make the cylinder look more like a pipe
ax.set_box_aspect((2, 1, 1))

# Adjust the view angle for better visibility
ax.view_init(elev=20, azim=-60)

# Show the plot
plt.tight_layout()
plt.savefig("double_helix.png", bbox_inches='tight') 
plt.show()