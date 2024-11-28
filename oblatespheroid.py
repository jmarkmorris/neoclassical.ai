import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec

def plot_spheroid(ax, a, c, title):
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    x = a * np.outer(np.cos(u), np.sin(v))
    y = a * np.outer(np.sin(u), np.sin(v))
    z = c * np.outer(np.ones_like(u), np.cos(v))

    ax.plot_wireframe(x, y, z, color='dimgray', alpha=0.7, linewidth=0.5)

    xx, yy = np.meshgrid(np.linspace(-1, 1, 10), np.linspace(-1, 1, 10))
    zz = np.zeros_like(xx)

    ax.plot_wireframe(xx, yy, zz, color='silver', alpha=0.7, linewidth=0.5)
    ax.plot_wireframe(zz, xx, yy, color='silver', alpha=0.7, linewidth=0.5)
    ax.plot_wireframe(xx, zz, yy, color='silver', alpha=0.7, linewidth=0.5)

    ax.plot([-1, 1], [0, 0], [0, 0], color='black', linewidth=0.5)
    ax.plot([0, 0], [-1, 1], [0, 0], color='black', linewidth=0.5)
    ax.plot([0, 0], [0, 0], [-1, 1], color='black', linewidth=0.5)

    ax.set_xlabel('X', labelpad=-15)
    ax.set_ylabel('Y', labelpad=-15)
    ax.set_zlabel('Z', labelpad=-15)

    ticks = [-1, -0.5, 0, 0.5, 1]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_zticks(ticks)

    def tick_formatter(value, pos):
        return f'{value:.1f}' if value != 0 else ''

    ax.xaxis.set_major_formatter(plt.FuncFormatter(tick_formatter))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(tick_formatter))
    ax.zaxis.set_major_formatter(plt.FuncFormatter(tick_formatter))

    ax.set_box_aspect((1,1,0.8))
    ax.axis('off')

    ax.set_title(title, fontsize=12, pad=0)  # Reduced title padding

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)

    ax.view_init(elev=20, azim=45)

# Set the figure size to match 2560x1664 pixels at 100 dpi
fig = plt.figure(figsize=(25.6, 16.64), dpi=100)

# Use GridSpec for more control over subplot layout
gs = gridspec.GridSpec(2, 5, figure=fig)
gs.update(wspace=0.02, hspace=0.02)  # Reduce space between subplots

ratios = [1.00, 0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10]

for i, ratio in enumerate(ratios):
    ax = fig.add_subplot(gs[i//5, i%5], projection='3d')
    a = 0.5
    c = a * ratio
    plot_spheroid(ax, a, c, f'c/a = {ratio:.2f}')

# Adjust the layout
plt.tight_layout(pad=0.5, h_pad=0.5, w_pad=0.5)

# Further adjust subplot parameters
plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)

# Save the figure with the exact pixel dimensions
plt.savefig('oblate_spheroids.png', dpi=100, bbox_inches='tight', pad_inches=0.1)
plt.show()
