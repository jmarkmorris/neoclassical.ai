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

class AngleObject(VGroup):
    def __init__(self, location=np.array([0, 0, 0]), **kwargs):
        super().__init__(**kwargs)

        self.location = location

        # Randomize colors
        line1_color = random.choice(MANIM_COLORS)
        line2_color = random.choice(MANIM_COLORS)
        while line2_color == line1_color:  # Ensure different colors for lines
            line2_color = random.choice(MANIM_COLORS)
        angle_arc_color = random.choice(MANIM_COLORS)
        dot_color = random.choice(MANIM_COLORS)
        theta_color = random.choice(MANIM_COLORS)

        # Define the initial and final angles in degrees
        initial_angle_deg = random.uniform(10, 170)  # Ensure non-zero initial angle
        final_angle_deg = random.uniform(190, 350)    # Ensure non-zero final angle

        # Create the first line
        self.line1 = Line(self.location, self.location + RIGHT, color=line1_color)
        # Create the second line, initially rotated to the initial angle
        self.line2 = Line(self.location, self.location + RIGHT, color=line2_color).rotate(
            initial_angle_deg * DEGREES, about_point=self.location
        )

        # Create the angle
        self.angle = Angle(self.line1, self.line2, radius=0.5, color=angle_arc_color)

        # Create a dot at the rotation center
        self.dot = Dot(point=self.location, color=dot_color)

        # Create the theta label
        self.theta_label = MathTex(r"\theta", color=theta_color).scale(0.7)

        # Add updater to the angle
        self.angle.add_updater(lambda a: a.become(Angle(self.line1, self.line2, radius=0.5, color=angle_arc_color)))

        # Add updater to the theta label
        def update_theta_label(obj):
            angle_obj = Angle(self.line1, self.line2, radius=0.5 + 3 * SMALL_BUFF)
            obj.move_to(angle_obj.point_from_proportion(0.5))

        self.theta_label.add_updater(update_theta_label)

        # Add the components to the VGroup
        self.add(self.line1, self.line2, self.angle, self.dot, self.theta_label)

        # Store the initial and final angles for animation
        self.initial_angle_deg = initial_angle_deg
        self.final_angle_deg = final_angle_deg

    def create_rotation_animation(self, run_time=3):
        return Rotate(
            self.line2,
            angle=(self.final_angle_deg - self.initial_angle_deg) * DEGREES,
            about_point=self.location,
            run_time=run_time
        )

class AnimatedAngle(Scene):
    def construct(self):
        self.camera.background_color = INDIGO

        # Create the first AngleObject
        angle1 = AngleObject(location=np.array([-3, 0, 0]))

        # Create the second AngleObject
        angle2 = AngleObject(location=np.array([3, 0, 0]))

        # Create the rotation animations
        rotate_animation1 = angle1.create_rotation_animation()
        rotate_animation2 = angle2.create_rotation_animation()

        # Add the AngleObjects to the scene
        self.add(angle1, angle2)

        # Play the rotation animations
        self.play(rotate_animation1, rotate_animation2)

        self.wait()
