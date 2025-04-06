from manim import *
import numpy as np
import random
# Import the AngleGroup from the npqg library
from npqg import AngleGroup

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"

# Manim standard colors list (replace dynamic generation with a static list)
MANIM_COLORS = [
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL, PINK, GOLD, MAROON,
    BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E,
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

        # --- Create First Angle ---
        location1 = np.array([-3, 0, 0])
        # Randomize colors
        line1_color_1 = random.choice(MANIM_COLORS)
        line2_color_1 = random.choice(MANIM_COLORS)
        while line2_color_1 == line1_color_1: line2_color_1 = random.choice(MANIM_COLORS)
        angle_arc_color_1 = random.choice(MANIM_COLORS)
        dot_color_1 = random.choice(MANIM_COLORS)
        theta_color_1 = random.choice(MANIM_COLORS)
        # Define angles
        initial_angle_deg_1 = random.uniform(10, 170)
        final_angle_deg_1 = random.uniform(190, 350)
        initial_alpha_1 = initial_angle_deg_1 / 360.0
        final_alpha_1 = final_angle_deg_1 / 360.0

        # Create a dummy path (a single point)
        path1 = Dot(location1, radius=0) # Invisible dot as path
        # Create AngleGroup instance
        angle1 = AngleGroup(initial_alpha=initial_alpha_1, path=path1, duration=1.0) # Duration doesn't matter here
        angle1.is_updating = False # Disable automatic updates
        angle1.set_color(
            line1_color=line1_color_1, line2_color=line2_color_1,
            arc_color=angle_arc_color_1, dot_color=dot_color_1, theta_color=theta_color_1
        )
        # Updater function for manual animation control
        def update_angle_anim_1(mob, alpha):
            mob._update_visuals(alpha)

        # --- Create Second Angle ---
        location2 = np.array([3, 0, 0])
        # Randomize colors
        line1_color_2 = random.choice(MANIM_COLORS)
        line2_color_2 = random.choice(MANIM_COLORS)
        while line2_color_2 == line1_color_2: line2_color_2 = random.choice(MANIM_COLORS)
        angle_arc_color_2 = random.choice(MANIM_COLORS)
        dot_color_2 = random.choice(MANIM_COLORS)
        theta_color_2 = random.choice(MANIM_COLORS)
        # Define angles
        initial_angle_deg_2 = random.uniform(10, 170)
        final_angle_deg_2 = random.uniform(190, 350)
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
        # Updater function for manual animation control
        def update_angle_anim_2(mob, alpha):
            mob._update_visuals(alpha)

        # Add AngleGroups to the scene
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

        # Play the animations
        self.play(animation1, animation2)

        self.wait()
