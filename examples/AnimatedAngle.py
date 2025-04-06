from manim import *
import numpy as np
import random
# Import the AngleGroup from the npqg library
from npqg import AngleGroup

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"

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

# Manim standard colors list (replace dynamic generation with a static list)
# Keep MANIM_COLORS definition if needed elsewhere, or remove if PASTEL_COLORS replaces it entirely.
# For this change, we'll use PASTEL_COLORS, so MANIM_COLORS is not strictly needed here.
MANIM_COLORS = [
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL, PINK, GOLD, MAROON,
    BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E, # Included for completeness if needed later
    TEAL_A, TEAL_B, TEAL_C, TEAL_D, TEAL_E,
    GREEN_A, GREEN_B, GREEN_C, GREEN_D, GREEN_E,
    YELLOW_A, YELLOW_B, YELLOW_C, YELLOW_D, YELLOW_E,
    GOLD_A, GOLD_B, GOLD_C, GOLD_D, GOLD_E,
    RED_A, RED_B, RED_C, RED_D, RED_E,
    MAROON_A, MAROON_B, MAROON_C, MAROON_D, MAROON_E,
    PURPLE_A, PURPLE_B, PURPLE_C, PURPLE_D, PURPLE_E,
    PINK, LIGHT_PINK, PURE_BLUE, PURE_GREEN, PURE_RED, LIGHT_BROWN, DARK_BROWN,
    # Add more colors as needed, ensuring they are valid Manim constants
]


class AnimatedAngle(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        run_time = 3
        start_scale_small = 0.2 # Initial scale for the growing angle
        end_scale_large = 1.2   # Final scale for the growing angle
        start_scale_large = 1.2   # Initial scale for the shrinking angle
        end_scale_small = 0.2   # Final scale for the shrinking angle


        # --- Create First Angle (Grows) ---
        location1 = np.array([-3, 0, 0])
        # Randomize colors using PASTEL_COLORS
        line1_color_1 = random.choice(PASTEL_COLORS)
        line2_color_1 = random.choice(PASTEL_COLORS)
        angle_arc_color_1 = random.choice(PASTEL_COLORS)
        dot_color_1 = random.choice(PASTEL_COLORS)
        theta_color_1 = random.choice(PASTEL_COLORS)
        # Define angles: Start small, grow to full 360 degrees
        initial_angle_deg_1 = random.uniform(10, 30)  # Small initial angle
        final_angle_deg_1 = 360.0                    # End at exactly 360 degrees
        initial_alpha_1 = initial_angle_deg_1 / 360.0
        final_alpha_1 = 1.0                          # Alpha for 360 degrees is 1.0

        # Create a dummy path (a single point)
        path1 = Dot(location1, radius=0) # Invisible dot as path
        # Create AngleGroup instance
        angle1 = AngleGroup(initial_alpha=initial_alpha_1, path=path1, duration=1.0) # Duration doesn't matter here
        angle1.is_updating = False # Disable automatic updates
        angle1.set_color(
            line1_color=line1_color_1, line2_color=line2_color_1,
            arc_color=angle_arc_color_1, dot_color=dot_color_1, theta_color=theta_color_1
        )
        # Updater function for manual angle animation control
        def update_angle_anim_1(mob, alpha):
            # Note: alpha here is the angle proportion (0 to 1)
            mob._update_visuals(alpha)

        # Updater function for manual scaling animation control
        def update_scale_anim_1(mob, alpha):
            # Note: alpha here is the animation progress (0 to 1)
            current_scale = interpolate(start_scale_small, end_scale_large, alpha)
            mob._set_scale_factor(current_scale)


        # --- Create Second Angle (Shrinks) ---
        location2 = np.array([3, 0, 0])
        # Randomize colors using PASTEL_COLORS
        line1_color_2 = random.choice(PASTEL_COLORS)
        line2_color_2 = random.choice(PASTEL_COLORS)
        angle_arc_color_2 = random.choice(PASTEL_COLORS)
        dot_color_2 = random.choice(PASTEL_COLORS)
        theta_color_2 = random.choice(PASTEL_COLORS)
        # Define angles: Start large, shrink small
        initial_angle_deg_2 = random.uniform(270, 350) # Large initial angle
        final_angle_deg_2 = random.uniform(10, 30)   # Small final angle
        initial_alpha_2 = initial_angle_deg_2 / 360.0
        final_alpha_2 = final_angle_deg_2 / 360.0

        # Create a dummy path
        path2 = Dot(location2, radius=0)
        # Create AngleGroup instance
        angle2 = AngleGroup(initial_alpha=initial_alpha_2, path=path2, duration=1.0)
        angle2.is_updating = False # Disable automatic updates
        angle2.set_color(
            line1_color=line1_color_2, line2_color=line2_color_2,
            arc_color=angle_arc_color_2, dot_color=dot_color_2, theta_color=theta_color_2
        )
        # Updater function for manual angle animation control
        def update_angle_anim_2(mob, alpha):
            # Note: alpha here is the angle proportion (0 to 1)
            mob._update_visuals(alpha)

        # Updater function for manual scaling animation control
        def update_scale_anim_2(mob, alpha):
            # Note: alpha here is the animation progress (0 to 1)
            current_scale = interpolate(start_scale_large, end_scale_small, alpha)
            mob._set_scale_factor(current_scale)


        # Add AngleGroups to the scene
        # Set initial scales before adding (or it will jump at frame 1 of animation)
        angle1._set_scale_factor(start_scale_small)
        angle2._set_scale_factor(start_scale_large)
        self.add(angle1, angle2)

        # Create the animations using UpdateFromAlphaFunc
        animation1 = UpdateFromAlphaFunc(
            angle1,
            update_angle_anim_1,
            alpha_range=(initial_alpha_1, final_alpha_1),
            run_time=run_time
        )
        animation2 = UpdateFromAlphaFunc(
            angle2,
            update_angle_anim_2,
            alpha_range=(initial_alpha_2, final_alpha_2),
            run_time=run_time
        )

        # Create the scaling animations using UpdateFromAlphaFunc
        scale_animation1 = UpdateFromAlphaFunc(
            angle1,
            update_scale_anim_1,
            run_time=run_time
            # alpha_range defaults to (0, 1) which is what we want for scaling progress
        )
        scale_animation2 = UpdateFromAlphaFunc(
            angle2,
            update_scale_anim_2,
            run_time=run_time
        )


        # Play all animations simultaneously
        self.play(animation1, animation2, scale_animation1, scale_animation2)

        self.wait()
