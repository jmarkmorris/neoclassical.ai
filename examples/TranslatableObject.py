from manim import *
import numpy as np

class TranslatableObject(Scene):
    def construct(self):
        # Define colors
        line1_color = BLUE
        line2_color = RED
        dot_color = GREEN
        theta_color = YELLOW
        angle_arc_color = WHITE

        # Define the rotation center
        rotation_center = np.array([0, 0, 0])

        # Create the first line
        line1 = Line(rotation_center, RIGHT, color=line1_color)

        # Create the second line
        line2 = Line(rotation_center, RIGHT, color=line2_color)

        # Create the angle
        angle = Angle(line1, line2, radius=0.5, color=angle_arc_color)

        # Create the theta label
        theta_label = MathTex(r"\theta", color=theta_color).scale(0.7)
        theta_label.move_to(angle.point_from_proportion(0.5))

        # Create a solid dot at the rotation center
        vertex_dot = Dot(
            point=rotation_center,
            radius=0.08,  # Adjust radius as needed
            color=dot_color
        )

        # Group elements
        moving_angle_group = VGroup(line1, line2, angle, theta_label, vertex_dot)

        # Define the rotation updater
        def update_angle(obj):
            v1 = line1.get_vector()
            v2 = line2.get_vector()
            angle_val = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
            obj.become(Angle(line1, line2, radius=0.5, color=angle_arc_color))
            theta_label.move_to(angle.point_from_proportion(0.5))

        # Define the rotation animation
        def rotate_line(line, angle=90 * DEGREES, rate_func=linear, run_time=3):
            line.rotate(angle, about_point=rotation_center)

        # Add the updater to the angle
        angle.add_updater(update_angle)

        # Add objects to the scene
        self.add(moving_angle_group)

        # Create the rotation animation
        rotate_animation = rotate_line(line2, angle=180 * DEGREES, run_time=5)

        # Create the translation animation
        translation_vector = np.array([4, 2, 0])
        translation_animation = moving_angle_group.animate.shift(translation_vector).set_run_time(5)

        # Play the animations simultaneously
        self.play(rotate_animation, translation_animation)

        # Wait
        self.wait()
