from manim import *
from tools import INDIGO
import numpy as np
import random
from manim.utils.space_ops import angle_between_vectors
from manim.utils.color import Colors

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

        # Create a group for the entire grid
        grid_group = VGroup()
        animations = []
        angle_elements = [] # To store elements for updater removal

        for row in range(rows):
            for col in range(cols):
                # Calculate position relative to grid center (0,0) for now
                x = x_start + col * x_spacing
                y = y_start - row * y_spacing
                position = np.array([x, y, 0])

                # Define the rotation center
                rotation_center = position + LEFT * 0.5

                # Randomize angles
                start_angle_deg = random.uniform(0, 360)
                end_angle_deg = random.uniform(0, 360)
                # Ensure end angle is different from start angle
                while abs(end_angle_deg - start_angle_deg) < 10:
                    end_angle_deg = random.uniform(0, 360)
                rotation_angle_deg = end_angle_deg - start_angle_deg

                # Randomize colors
                line1_color = random.choice(MANIM_COLORS)
                line2_color = random.choice(MANIM_COLORS)
                while line2_color == line1_color: # Ensure different colors for lines
                    line2_color = random.choice(MANIM_COLORS)
                dot_color = random.choice(MANIM_COLORS)
                theta_color = random.choice(MANIM_COLORS)
                angle_arc_color = random.choice(MANIM_COLORS)

                # Randomize rate function (30% chance of reversing)
                if random.random() < 0.3:
                    rate_func = there_and_back
                else:
                    rate_func = linear # or smooth

                # Create the first line
                line1 = Line(rotation_center, position + RIGHT * 0.5, color=line1_color)
                # Create the second line, rotated to the random start angle
                line2 = Line(rotation_center, position + RIGHT * 0.5, color=line2_color).rotate(
                    start_angle_deg * DEGREES, about_point=rotation_center
                )
                # Create the angle
                angle = Angle(line1, line2, radius=0.5, color=angle_arc_color)
                # Create the theta label
                theta_label = MathTex(r"\theta", color=theta_color).scale(0.7)
                theta_label.move_to(
                    Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
                )
                # Create a dot at the rotation center
                dot = Dot(rotation_center, color=dot_color, radius=0.08)

                # Group elements for this cell
                cell_group = VGroup(line1, line2, angle, theta_label, dot)
                grid_group.add(cell_group)
                angle_elements.append((angle, theta_label)) # Store for updater removal

                # Create the animation
                rotate_action = Rotate(
                    line2,
                    angle=rotation_angle_deg * DEGREES,
                    about_point=rotation_center,
                    rate_func=rate_func,
                    run_time=random.uniform(3, 7), # Randomize duration
                )
                animations.append(rotate_action)

                # Create the updater for the angle and theta label
            # Need to use a function factory or lambda with default arguments
            # Capture correct variables AND the angle arc color for each angle's updater
            def create_update_angle(l1, l2, arc_color):
                def update_angle(obj):
                    v1 = l1.get_vector()
                    v2 = l2.get_vector()
                    # Check if vectors are non-zero before calculating angle
                    if np.linalg.norm(v1) > 1e-6 and np.linalg.norm(v2) > 1e-6:
                        angle_val = angle_between_vectors(v1, v2)
                        # Check if lines are parallel (angle close to 0 or PI)
                        if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
                            obj.become(Angle(l1, l2, radius=0.5, color=arc_color))
                            obj.set_opacity(1) # Ensure visible
                        else:
                            obj.set_opacity(0) # Hide if parallel or coincident
                    else:
                        obj.set_opacity(0) # Hide if vectors are zero
                return update_angle

            def create_update_theta_label(l1, l2):
                def update_theta_label(obj):
                    v1 = l1.get_vector()
                    v2 = l2.get_vector()
                     # Check if vectors are non-zero before calculating angle
                    if np.linalg.norm(v1) > 1e-6 and np.linalg.norm(v2) > 1e-6:
                        angle_val = angle_between_vectors(v1, v2)
                        # Check if lines are parallel (angle close to 0 or PI)
                        if angle_val > ANGLE_EPSILON and abs(angle_val - PI) > ANGLE_EPSILON:
                            temp_angle = Angle(l1, l2, radius=0.5 + 3 * SMALL_BUFF)
                            obj.move_to(temp_angle.point_from_proportion(0.5))
                            obj.set_opacity(1) # Ensure visible
                        else:
                            obj.set_opacity(0) # Hide if parallel or coincident
                    else:
                         obj.set_opacity(0) # Hide if vectors are zero
                return update_theta_label

            # Add the updaters to the angle and theta label
            angle.add_updater(create_update_angle(line1, line2, angle_arc_color))
            theta_label.add_updater(create_update_theta_label(line1, line2))

        # Center the entire grid group
        grid_group.move_to(ORIGIN)
        self.add(grid_group) # Add the centered group to the scene

        # Play all animations simultaneously
        self.play(*animations)

        # Remove the updaters after animation is complete
        for angle_obj, label_obj in angle_elements:
             angle_obj.clear_updaters()
             label_obj.clear_updaters()

        self.wait()
