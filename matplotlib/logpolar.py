import matplotlib.pyplot as plt
import numpy as np

# Define the radius limits for each band
radii = [1, 10, 100, 1000]

# Define radii for red circles
red_circle_radii = [i for i in range(2, 10)] + [i * 10 for i in range(2, 10)] + [i * 100 for i in range(2, 10)]

# Create a figure and polar axes
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

# Generate theta values for the bands
theta = np.linspace(0, 2 * np.pi, 100)

# Plot the bands
for radius in radii:
    ax.plot(theta, np.full_like(theta, radius), color='purple', linestyle='-', alpha=0.2) 

# Plot red circles
for radius in red_circle_radii:
    ax.plot(theta, np.full_like(theta, radius), color='purple', linestyle=':', linewidth=0.5) 

# Set the radial scale to logarithmic
ax.set_rscale('log')

# Set the radial limits
ax.set_rlim(radii[0], radii[-1])

# Set theta ticks and labels in radians
ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2])
ax.set_xticklabels(['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$'], color='purple')

# Customize the plot (optional)
# ax.set_title('Polar Plot with Logarithmic Radius', color='purple') 
ax.grid(True, color='purple')

# Set figure and axes background transparent
fig.patch.set_alpha(0) 
ax.patch.set_alpha(0) 

# Save the figure
plt.savefig('logpolar.svg', dpi=300)
plt.savefig('logpolar.png', dpi=300)

# Show the plot
plt.show()