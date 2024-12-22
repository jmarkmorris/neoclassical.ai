import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create a new figure
fig = plt.figure(figsize=(16, 9))  # Increased figure size
ax = fig.add_subplot(111, projection='3d')

# Parameters for the cylinder
length = 80  # Length of the cylinder
initial_radius = 4   # Initial radius of the cylinder
radius_reduction = 0.1  # 10% radius reduction
num_segments = 10

# Create the cylinder coordinates (horizontal pipe)
theta = np.linspace(0, 2 * np.pi, 100)
x = np.linspace(0, length, 100)  # Along x-axis
theta, x = np.meshgrid(theta, x)
y = initial_radius * np.cos(theta)
z = initial_radius * np.sin(theta)

# Plot the cylinder surface with reduced shading
ax.plot_surface(x, y, z, color='lightblue', alpha=0.3)  # Reduced alpha for less shading

# Function to generate double helix data with variable frequency and radius
def generate_helix(cycles, offset, radius):
  t = np.linspace(offset, length + offset, 1000)
  x_helix = t
  y_helix1 = radius * np.cos(2 * np.pi * (t - offset) / length * cycles)
  z_helix1 = radius * np.sin(2 * np.pi * (t - offset) / length * cycles)
  y_helix2 = radius * np.cos(2 * np.pi * (t - offset) / length * cycles + np.pi)
  z_helix2 = radius * np.sin(2 * np.pi * (t - offset) / length * cycles + np.pi)
  return x_helix, y_helix1, z_helix1, y_helix2, z_helix2

# Initialize offset for appending helices
offset = 0

# Generate and plot double helices with increasing frequencies, decreasing radius, and alternating colors
for cycles in range(1, num_segments + 1):  # Iterate from 1 to 10 segments
  x_helix, y_helix1, z_helix1, y_helix2, z_helix2 = generate_helix(cycles, offset, initial_radius)
  ax.plot(x_helix, y_helix1, z_helix1, color='red' if cycles % 2 == 1 else 'blue', linewidth=0.5)
  ax.plot(x_helix, y_helix2, z_helix2, color='blue' if cycles % 2 == 1 else 'red', linewidth=0.5)
  offset += length  # Increase offset by full length
  initial_radius *= (1 - radius_reduction)  # Reduce radius for the next helix

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
ax.view_init(elev=10, azim=-80)

# Show the plot
plt.tight_layout()
plt.savefig("double_helix.svg", bbox_inches='tight') 
plt.show()
