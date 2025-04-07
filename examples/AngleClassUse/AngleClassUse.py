import random
from manim import *
import numpy as np
# Import the AngleGroup from the npqg library
from npqg import AngleGroup

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
                dot_color=random.choice(PASTEL_COLORS)
            )
            angle_groups.append(angle_group)

            # Add updater using the lambda function for consistency
            angle_group.add_updater(lambda mob, dt: mob.update(dt))

        # Add all paths and angle groups to the scene
        self.add(*paths)
        self.add(*angle_groups)

        # --- Trigger dynamic scaling with new time-based method
        if angle_groups: # Ensure there's at least one group
            # Demonstrate precise time-based scaling with start and end times
            # First group: Scale to 0.5x from 0 to 10 seconds
            angle_groups[0].dynamic_scale(0, 10, 0.5)
            
            # Apply scaling to other angle groups with different scales and timings
            for i, group in enumerate(angle_groups[1:], 1):
                if i % 3 == 0:
                    # Scale to 0.7x from 5 to 13 seconds
                    group.dynamic_scale(5, 13, 0.7)
                elif i % 3 == 1:
                    # Scale to 0.4x from 8 to 20 seconds
                    group.dynamic_scale(8, 20, 0.4)
                else:
                    # Scale to 0.6x from 3 to 12 seconds
                    group.dynamic_scale(3, 12, 0.6)

        # Wait until the angle reaches 225 degrees (0.625 * 15s = 9.375s)
        pause_time = (225 / 360) * animation_duration
        self.wait(pause_time)
        
        # Demonstrate pause/resume functionality
        # Pause all animations
        for group in angle_groups:
            group.pause_animation()
        
        # Display a message indicating the pause
        pause_text = Text("Animation Paused", color=WHITE).to_edge(UP)
        self.play(FadeIn(pause_text))
        self.wait(1)
        
        # Resume all animations
        for group in angle_groups:
            group.resume_animation()
            
        # Update the message
        resume_text = Text("Animation Resumed", color=WHITE).to_edge(UP)
        self.play(Transform(pause_text, resume_text))
        
        # Wait for the remaining animation time (15s - 9.375s = 5.625s)
        remaining_time = animation_duration - pause_time
        self.wait(remaining_time)
        
        # Optional: Remove updaters from all angle groups after the main animation
        for group in angle_groups:
            # Need to be careful removing lambda updaters; storing them might be safer.
            # However, for this simple case, clearing all updaters works.
            group.clear_updaters() # Simpler way to remove all updaters
            
        # Fade out the text
        self.play(FadeOut(pause_text))

        # Wait for a moment at the end
        self.wait(2)
