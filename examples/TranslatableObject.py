from manim import *
import numpy as np
import random
from tools import INDIGO

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

        # Define the rotation center
        rotation_center = np.array([0, 0, 0])

        # Define the initial and final angles in degrees
        initial_angle_deg = random.uniform(10, 170)  # Ensure non-zero initial angle
        final_angle_deg = random.uniform(190, 350)    # Ensure non-zero final angle

        # Randomize colors
        line1_color = random.choice(MANIM_COLORS)
        line2_color = random.choice(MANIM_COLORS)
        while line2_color == line1_color: # Ensure different colors for lines
            line2_color = random.choice(MANIM_COLORS)
        angle_arc_color = random.choice(MANIM_COLORS)

        # Create the first line
        line1 = Line(rotation_center, RIGHT, color=line1_color)
        # Create the second line, initially rotated to the initial angle
        line2 = Line(rotation_center, RIGHT, color=line2_color).rotate(initial_angle_deg * DEGREES, about_point=rotation_center)

        # Create the angle
        angle = Angle(line1, line2, radius=0.5, color=angle_arc_color)

        # Create the animation for line2 to rotate to the final angle
        rotate_animation = Rotate(
            line2,
            angle=(final_angle_deg - initial_angle_deg) * DEGREES,
            about_point=rotation_center,
            run_time=3
        )

        # Add the lines and angle to the scene
        self.add(line1, line2, angle)

        # Play the rotation animation
        self.play(rotate_animation)

        self.wait()
