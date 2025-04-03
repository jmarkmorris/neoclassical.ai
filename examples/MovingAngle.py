from manim import *
from tools import INDIGO
import numpy as np
from manim.utils.space_ops import angle_between_vectors

# Define a small epsilon to avoid floating point issues near PI
ANGLE_EPSILON = 1e-6

class MovingAngle(Scene): # Renamed class to match filename
    def construct(self):
        self.camera.background_color = INDIGO

        # Add title
        title = Text("Moving Angle Grid", font="Helvetica Neue", weight="LIGHT", font_size=36)
        title.to_edge(UP, buff=0.5)
        self.add(title)

        # Grid parameters
        rows = 3
        cols = 4
        x_spacing = 3
        y_spacing = 2
        x_start = -((cols - 1) * x_spacing) / 2
        y_start = ((rows - 1) * y_spacing) / 2

        # Colors for lines and dots
        line_colors = [BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, TEAL, PINK, MAROON, GOLD, BLUE_A, GREEN_A] # Replaced LIME with GREEN_A
        dot_colors = [WHITE, GRAY, BLACK, DARK_GRAY, DARKER_GRAY, LIGHT_GRAY, LIGHTER_GRAY, RED_A, RED_B, RED_C, RED_D, RED_E]

        # Create and position the moving angles
        angles = []
        animations = []
        for row in range(rows):
            for col in range(cols):
                # Calculate position
                x = x_start + col * x_spacing
                y = y_start - row * y_spacing
                position = np.array([x, y, 0])

                # Define the rotation center
                rotation_center = position + LEFT * 0.5

                # Create the first line
                line1 = Line(rotation_center, position + RIGHT * 0.5, color=line_colors[(row * cols + col) % len(line_colors)])
                # Create the second line, initially at 30 degrees
                line2 = Line(rotation_center, position + RIGHT * 0.5, color=line_colors[(row * cols + col + 1) % len(line_colors)]).rotate(
                    30 * DEGREES, about_point=rotation_center
                )
                # Create the angle, initially at 30 degrees
                angle = Angle(line1, line2, radius=0.5, color=YELLOW)
                # Create the theta label
                theta_label = MathTex(r"\theta").scale(0.7)
                theta_label.move_to(
                    Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
                )
                # Create a dot at the rotation center
                dot = Dot(rotation_center, color=dot_colors[(row * cols + col) % len(dot_colors)], radius=0.08)

                # Store the angle elements
                angles.append((line1, line2, angle, theta_label, dot, rotation_center))

                # Add the objects to the scene
                self.add(line1, line2, angle, theta_label, dot)

        # Animate the angles
        for line1, line2, angle, theta_label, dot, rotation_center in angles:
            # Create the animation to rotate line2 to 330 degrees
            rotate_action = Rotate(
                line2,
                angle=300 * DEGREES,  # Rotate by 300 degrees (330 - 30)
                about_point=rotation_center,
                run_time=5,
            )
            animations.append(rotate_action)

            # Create the updater for the angle and theta label
            # Need to use a function factory or lambda with default arguments
            # to capture the correct variables for each angle's updater
            def create_update_angle(l1, l2):
                def update_angle(obj):
                    # Check if lines are parallel (angle close to PI)
                    v1 = l1.get_vector()
                    v2 = l2.get_vector()
                    angle_val = angle_between_vectors(v1, v2)
                    if abs(angle_val - PI) > ANGLE_EPSILON:
                         obj.become(Angle(l1, l2, radius=0.5, color=YELLOW))
                    # Optionally hide the angle object when lines are parallel
                    # else:
                    #     obj.set_opacity(0)
                return update_angle

            def create_update_theta_label(l1, l2):
                def update_theta_label(obj):
                    # Check if lines are parallel (angle close to PI)
                    v1 = l1.get_vector()
                    v2 = l2.get_vector()
                    angle_val = angle_between_vectors(v1, v2)
                    if abs(angle_val - PI) > ANGLE_EPSILON:
                        # Ensure angle object exists before calculating position
                        temp_angle = Angle(l1, l2, radius=0.5 + 3 * SMALL_BUFF)
                        obj.move_to(temp_angle.point_from_proportion(0.5))
                        # obj.set_opacity(1) # Make visible if previously hidden
                    # Optionally hide the label object when lines are parallel
                    # else:
                    #     obj.set_opacity(0)
                return update_theta_label

            # Add the updaters to the angle and theta label
            angle.add_updater(create_update_angle(line1, line2))
            theta_label.add_updater(create_update_theta_label(line1, line2))

        # Play all animations simultaneously
        self.play(*animations)

        # Remove the updaters after animation
        for _, _, angle_obj, label_obj, _, _ in angles:
             angle_obj.clear_updaters()
             label_obj.clear_updaters()

        self.wait()
