from manim import *
import numpy as np
import random
from manim.utils.space_ops import angle_between_vectors

# Define a small epsilon to avoid floating point issues near PI
ANGLE_EPSILON = 1e-6

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

class TranslatableObject(Scene):
    def construct(self):
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

        # Define the rotation center
        rotation_center = np.array([0, 0, 0])

        # Create the first line
        line1 = Line(rotation_center, RIGHT * 0.5, color=line1_color)
        # Create the second line, rotated to the random start angle
        line2 = Line(rotation_center, RIGHT * 0.5, color=line2_color).rotate(
            start_angle_deg * DEGREES, about_point=rotation_center
        )
        # Create the angle
        angle = Angle(line1, line2, radius=0.5, color=angle_arc_color)
        # Create the theta label
        theta_label = MathTex(r"\theta", color=theta_color).scale(0.7)

        # Create a solid dot at the rotation center
        vertex_dot = Dot(
            point=rotation_center,
            radius=0.08, # Adjust radius as needed
            color=dot_color
        )

        # Group elements for this cell
        moving_angle_group = VGroup(line1, line2, angle, theta_label, vertex_dot)

        # --- Define Updater Factories Once ---
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
        # --- End Updater Factories ---

        # Add the updaters to the angle and theta label
        angle_updater = create_update_angle(line1, line2, angle_arc_color)
        theta_label_updater = create_update_theta_label(line1, line2)
        angle.add_updater(angle_updater)
        theta_label.add_updater(theta_label_updater)

        # Position theta_label initially and check visibility
        initial_theta_pos_angle = Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF)
        v1_init = line1.get_vector()
        v2_init = line2.get_vector()
        if np.linalg.norm(v1_init) > 1e-6 and np.linalg.norm(v2_init) > 1e-6:
            angle_val_init = angle_between_vectors(v1_init, v2_init)
            if angle_val_init > ANGLE_EPSILON and abs(angle_val_init - np.pi) > ANGLE_EPSILON:
                 theta_label.move_to(initial_theta_pos_angle.point_from_proportion(0.5))
            else:
                 # Hide label and angle arc if initially parallel/coincident
                 theta_label.set_opacity(0)
                 angle.set_opacity(0)
        else:
             # Hide label and angle arc if vectors are zero
             theta_label.set_opacity(0)
             angle.set_opacity(0)

        # Create the animation
        rotate_action = Rotate(
            line2,
            angle=rotation_angle_deg * DEGREES,
            about_point=rotation_center,
            run_time=5, # Randomize duration
        )

        # Create the translation animation
        translation_vector = np.array([4, 2, 0])
        translation_animation = moving_angle_group.animate.shift(translation_vector).set_run_time(5)

        # Add the final grid group to the scene
        self.add(moving_angle_group)

        # Play all animations simultaneously
        self.play(rotate_action, translation_animation)

        self.wait()
