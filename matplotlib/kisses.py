#
# it would be nice to make the background planes disappear
# this shows static trails - is there a way to make them more dynamic?
# show red and blue spheres on the x-y plane for current position
# 
# 
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def generate_1z_curve(x0, y0, positive=True, scale=1):
    theta = np.linspace(0, 2*np.pi, 100)
    if positive:
        z = np.linspace(0.1, scale, 100)
    else:
        z = np.linspace(-scale, -0.1, 100)
    theta, z = np.meshgrid(theta, z)
    
    r = scale / (20 * np.abs(z))  # This creates the 1/z relationship
    X = x0 + r * np.cos(theta)
    Y = y0 + r * np.sin(theta)
    Z = z
    
    return X, Y, Z

# Parameters
num_curves = 12  # Number of curves to generate
scale = 10  # Scale parameter: axes will range from -scale to +scale
elev_angle = 20  # Elevation angle for viewing
azim_angle = 30   # Azimuthal angle for viewing

# Create figure and 3D axis
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Create shaded planes at x=0, y=0, and z=0
xx, yy = np.meshgrid(np.linspace(-scale, scale, 10), np.linspace(-scale, scale, 10))
ax.plot_surface(xx, yy, np.zeros_like(xx), alpha=0.1, color='gray')  # z=0 plane
ax.plot_surface(np.zeros_like(xx), yy, xx, alpha=0.1, color='gray')  # x=0 plane
ax.plot_surface(xx, np.zeros_like(xx), yy, alpha=0.1, color='gray')  # y=0 plane

# Generate random 1/z curves
np.random.seed(42)  # For reproducibility

for _ in range(num_curves):
    x0 = np.random.uniform(-scale, scale)
    y0 = np.random.uniform(-scale, scale)
    positive = np.random.choice([True, False])
    
    X, Y, Z = generate_1z_curve(x0, y0, positive, scale)
    
    if positive:
        color = '#FF0000'  # Fire engine red
    else:
        color = '#4169E1'  # Royal blue
    
    ax.plot_surface(X, Y, Z, color=color, alpha=0.7)

# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title(f'{num_curves} 1/z Curves in Linear Polar Coordinates')

# Set axis limits
ax.set_xlim(-scale, scale)
ax.set_ylim(-scale, scale)
ax.set_zlim(-scale, scale)

# Adjust view angle using parameterized angles
ax.view_init(elev=elev_angle, azim=azim_angle)

# Show plot
plt.tight_layout()
plt.show()
