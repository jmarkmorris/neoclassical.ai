import random
from manim import *
import numpy as np
# Import the AngleGroup from the npqg library
from npqg import AngleGroup

# Define the updater function separately
def angle_group_updater(mobject, dt, *args): # Add *args to accept extra positional args
    """Updater function passed to Manim's add_updater.
    Accepts potential extra arguments from Manim but only uses mobject and dt
    to call the mobject's own update method.
    """
    # Explicitly call update with only dt, ignoring any extra args Manim might send
    mobject.update(dt)

# Colors used specifically by the AnglesMoving Scene
INDIGO = "#4B0082"

# Define a list of Manim pastel colors
PASTEL_COLORS = [
    BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E,
    TEAL_A, TEAL_B, TEAL_C, TEAL_D, TEAL_E,
    GREEN_A, GREEN_B, GREEN_C, GREEN_D, GREEN_E,
    YELLOW_A, YELLOW_B, YELLOW_C, YELLOW_D, YELLOW_E,
    GOLD_A, GOLD_B, GOLD_C, GOLD_D, GOLD_E,
    RED_A, RED_B, RED_C, RED_D, RED_E,
    MAROON_A, MAROON_B, MAROON_C, MAROON_D, MAROON_E,
    PURPLE_A, PURPLE_B, PURPLE_C, PURPLE_D, PURPLE_E,
    PINK
]

# The Scene class remains here for now, acting as an example usage
class AngleClassUse(Scene):
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
        start_y = (num_rows - 1) * shift_distance_y / 2 - 0.3 

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
            # Set an independently chosen random pastel color for each component
            angle_group.set_color(
                line1_color=random.choice(PASTEL_COLORS),
                line2_color=random.choice(PASTEL_COLORS),
                arc_color=random.choice(PASTEL_COLORS),
                dot_color=random.choice(PASTEL_COLORS),
                theta_color=random.choice(PASTEL_COLORS)
            )
            angle_groups.append(angle_group)

            # Add updater using the named function
            angle_group.add_updater(angle_group_updater)

        # Add all paths and angle groups to the scene
        self.add(*paths)
        self.add(*angle_groups)

        # --- Trigger dynamic scaling for the top-left angle (index 0) ---
        # Scale it down to 50% over 10 seconds, starting immediately.
        # This happens concurrently with the angle animation via the updater.
        if angle_groups: # Ensure there's at least one group
            self.play(
                # General scaling: target_scale=0.5, duration=10.0 seconds
                ApplyMethod(angle_groups[0].dynamic_scale, 0.5, 10.0),
                run_time=0.1 # Start the scaling setup quickly
            )

        # Wait for the initial angle animation (and the concurrent scaling) to complete
        self.wait(animation_duration)

        # --- Remove the previous example that scaled all groups afterwards ---
        # (Code block removed)


        # Optional: Remove updaters from all angle groups after the main animation
        for group in angle_groups:
            # Need to be careful removing lambda updaters; storing them might be safer.
            # However, for this simple case, clearing all updaters works.
            group.clear_updaters() # Simpler way to remove all updaters

        # Wait for a moment at the end
        self.wait(2)
