from manim import *
import numpy as np
from manim.utils.space_ops import angle_between_vectors

# Define a small epsilon to avoid floating point issues near PI
ANGLE_EPSILON = 1e-6

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
            # Check if vectors are non-zero before calculating angle
            if np.linalg.norm(v1) > 1e-6 and np.linalg.norm(v2) > 1e-6:
                angle_val = angle_between_vectors(v1, v2)
                # Check if lines are parallel (angle close to 0 or PI)
                if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
                    obj.become(Angle(line1, line2, radius=0.5, color=angle_arc_color))
                    obj.set_opacity(1)  # Ensure visible
                    theta_label.move_to(angle.point_from_proportion(0.5))
                    theta_label.set_opacity(1) # Ensure visible
                else:
                    obj.set_opacity(0)  # Hide if parallel or coincident
                    theta_label.set_opacity(0) # Hide if parallel or coincident
            else:
                obj.set_opacity(0) # Hide if vectors are zero
                theta_label.set_opacity(0) # Hide if vectors are zero

        # Define the rotation animation
        def rotate_line(line, angle=90 * DEGREES, rate_func=linear, run_time=3):
            line.rotate(angle, about_point=rotation_center)

        # Add the updater to the angle
        angle.add_updater(update_angle)

        # Position theta_label initially and check visibility
        v1_init = line1.get_vector()
        v2_init = line2.get_vector()
        if np.linalg.norm(v1_init) > 1e-6 and np.linalg.norm(v2_init) > 1e-6:
            angle_val_init = angle_between_vectors(v1_init, v2_init)
            if angle_val_init > ANGLE_EPSILON and abs(angle_val_init - np.pi) > ANGLE_EPSILON:
                theta_label.move_to(angle.point_from_proportion(0.5))
            else:
                # Hide label and angle arc if initially parallel/coincident
                theta_label.set_opacity(0)
                angle.set_opacity(0)
        else:
            # Hide label and angle arc if vectors are zero
            theta_label.set_opacity(0)
            angle.set_opacity(0)

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
