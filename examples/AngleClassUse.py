import sys
import os
print("--- Python sys.path ---")
print(sys.path)
print("--- Current Working Directory ---")
print(os.getcwd())
print("--- npqg expected location ---")
# Assuming the script is run from the project root or similar
# Adjust the path calculation if needed based on CWD output
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(os.path.join(project_root, 'npqg'))

# --- Add project root to sys.path ---
if project_root not in sys.path:
    print(f"--- Adding {project_root} to sys.path ---")
    sys.path.insert(0, project_root)
else:
    print(f"--- {project_root} already in sys.path ---")
# --- End of addition ---

print("--- Attempting import ---")

from manim import *
import numpy as np
# Import the AngleGroup from the new library structure
# Use absolute import assuming 'npqg' is in the Python path or CWD
try:
    # Import directly from the package thanks to npqg/__init__.py
    from npqg import AngleGroup
    print("--- Import successful ---")
except ModuleNotFoundError as e:
    print(f"--- Import failed: {e} ---")
    # Re-raise the exception so Manim still shows the error
    raise e

# Colors used specifically by the AnglesMoving Scene
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
# WHITE is also defined in mobjects.py, but keeping it here is fine if other
# elements in this scene might use it independently. If not, it could be removed.
WHITE = "#FFFFFF"


# The Scene class remains here for now, acting as an example usage
class AnglesClassUse(Scene):
    def construct(self):

        self.camera.background_color = INDIGO

        # Define parameters
        circle_radius = 0.4 
        shift_distance_x = 3.2    # Increased Horizontal distance between columns
        shift_distance_y = 2.4    # Vertical distance between rows (adjust as needed)
        initial_alpha = 0.001     # Start slightly off 0 to avoid initial degenerate angle
        animation_duration = 15.0
        num_rows = 3
        num_cols = 4

        # Calculate the starting position for the grid (top-left)
        # Center the grid horizontally: total_width = (num_cols - 1) * shift_distance_x
        # Center the grid vertically: total_height = (num_rows - 1) * shift_distance_y
        start_x = - (num_cols - 1) * shift_distance_x / 2
        start_y = (num_rows - 1) * shift_distance_y / 2 - 0.3 # Shift grid down by 0.5, then up by 0.2

        # Define center points for the 3x4 grid using loops
        centers = []
        for r in range(num_rows):
            for c in range(num_cols):
                center_x = start_x + c * shift_distance_x
                base_center_y = start_y - r * shift_distance_y
                # Apply row-specific vertical shifts
                if r == 1: # Row 2 (0-indexed)
                    adjusted_center_y = base_center_y + 0.1
                elif r == 2: # Row 3 (0-indexed)
                    adjusted_center_y = base_center_y + 0.2
                else: # Row 1 (r=0) or any other rows
                    adjusted_center_y = base_center_y
                centers.append(np.array([center_x, adjusted_center_y, 0]))

        # Define colors for paths (ensure enough colors or allow cycling)
        path_colors = [
            YELLOW_A, GREEN_A, RED_A, BLUE_A,
            PURPLE_A, ORANGE, PINK, TEAL_A,
            GOLD_A, MAROON_A, LIGHT_GREY, WHITE
        ]

        paths = []
        angle_groups = []

        # Create paths and angle groups for each center point
        for i, center in enumerate(centers):
            path = ParametricFunction(
                lambda t, c=center: np.array([
                    circle_radius * np.cos(t) + c[0], # x-coordinate
                    circle_radius * np.sin(t) + c[1], # y-coordinate
                    c[2]                              # z-coordinate (remains 0)
                ]),
                t_range=[0, TAU],
                color=path_colors[i % len(path_colors)], # Cycle through colors
                stroke_opacity=0.3
            )
            paths.append(path)

            angle_group = AngleGroup(initial_alpha, path, duration=animation_duration)
            angle_groups.append(angle_group)

            # Add updater to the angle group
            angle_group.add_updater(lambda mob, dt: mob.update(dt))

        # Add all paths and angle groups to the scene
        self.add(*paths)
        self.add(*angle_groups)

        # Wait for the duration of the animation for the updaters to run
        self.wait(animation_duration)

        # Optional: Remove updaters from all angle groups
        for group in angle_groups:
            # Need to be careful removing lambda updaters; storing them might be safer.
            # However, for this simple case, clearing all updaters works.
            group.clear_updaters() # Simpler way to remove all updaters

        # Wait for a moment at the end
        self.wait(2)
