from manim import *
import numpy as np

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
WHITE = "#FFFFFF"

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    norm = np.linalg.norm(vector)
    if norm == 0:
       return vector # Return zero vector if input is zero vector
    return vector / norm

# Reusable Angle Group Class
class AngleGroup(VGroup):
    def __init__(self, initial_position, initial_angle_value, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path # Store the path for the updater

        # Define points for the angle
        A = np.array([1, 0, 0])
        O = np.array([0, 0, 0]) # Relative origin for angle calculation
        B = np.array([np.cos(initial_angle_value), np.sin(initial_angle_value), 0])

        # Create components relative to the initial position
        self.line1 = Line(initial_position, initial_position + A, color=GREEN)
        self.line2 = Line(initial_position, initial_position + B, color=ORANGE)
        # Ensure fill opacity is 0 from the start
        self.angle_obj = Angle(self.line1, self.line2, radius=0.8, color=BLUE_C, dot=True, dot_radius=0.07, dot_distance=0, fill_opacity=0)
        self.theta = MathTex(r"\theta", color=WHITE).scale(0.6)

        # Initial theta position calculation
        line_length = 1.0 # Since A is unit vector

        # Alternative theta positioning
        A_vec = A
        B_vec = B
        mid_vector = (A_vec + B_vec) / 2
        mid_vector_norm = np.linalg.norm(mid_vector)
        if mid_vector_norm > 1e-6:
            unit_mid_vector = mid_vector / mid_vector_norm
            theta_pos = initial_position + unit_mid_vector * 1.1 * line_length
        else:
            # Handle degenerate case
            default_offset_vector = A_vec / np.linalg.norm(A_vec)
            theta_pos = initial_position + default_offset_vector * 1.1 * line_length
        self.theta.move_to(theta_pos)

        # Add components to the VGroup
        self.add(self.line1, self.line2, self.angle_obj, self.theta)

    # Updater function moved inside the class
    def update_components(self, alpha):
        position = self.path.point_from_proportion(alpha)
        angle_value = alpha * 360 * DEGREES

        # Define new vectors relative to origin
        A_vec = np.array([1, 0, 0])
        B_vec = np.array([np.cos(angle_value), np.sin(angle_value), 0])

        # Update lines
        self.line1.put_start_and_end_on(position, position + A_vec)
        self.line2.put_start_and_end_on(position, position + B_vec)

        # Check for parallel/anti-parallel lines (angle near 0, 180, 360 deg)
        # Use a small tolerance (atol) for floating point comparisons
        is_degenerate = np.isclose(angle_value % PI, 0, atol=1e-6) or np.isclose(angle_value % PI, PI, atol=1e-6)

        if not is_degenerate:
            # Update angle object only if lines are not parallel/anti-parallel
            try:
                # Ensure new angle also has no fill
                # Use a temporary Angle to avoid modifying self.angle_obj before checking validity
                temp_angle = Angle(self.line1, self.line2, radius=0.8, color=BLUE_C, dot=True, dot_radius=0.07, dot_distance=0, fill_opacity=0)
                self.angle_obj.become(temp_angle)
                # Explicitly set stroke opacity, keep fill opacity at 0
                self.angle_obj.set_stroke(opacity=1)
            except ValueError:
                # This should ideally not happen due to the is_degenerate check, but as a safeguard:
                is_degenerate = True # Treat as degenerate if Angle() fails

        # Check is_degenerate *again* because the try-except might have changed it
        if not is_degenerate:
            # Calculate theta position safely only if angle is valid
            line_length = 1.0 # Since A_vec is unit vector

            # Alternative theta positioning
            mid_vector = (A_vec + B_vec) / 2
            mid_vector_norm = np.linalg.norm(mid_vector)
            if mid_vector_norm > 1e-6:
                unit_mid_vector = mid_vector / mid_vector_norm

                # Check if angle is greater than 180 degrees (PI radians)
                if angle_value > PI:
                    unit_mid_vector = -unit_mid_vector  # Flip the direction

                theta_pos = position + unit_mid_vector * 1.1 * line_length
                self.theta.move_to(theta_pos)
                self.theta.set_opacity(1)
                # angle_obj opacity was set to 1 in the try block above
            else:
                # Handle degenerate case (mid_vector is zero)
                default_offset_vector = A_vec / np.linalg.norm(A_vec) # Use A_vec direction
                theta_pos = position + default_offset_vector * 1.1 * line_length
                self.theta.move_to(theta_pos)
                self.theta.set_opacity(1) # Keep theta visible
                # angle_obj opacity was set to 1 in the try block above
        else:
            # Handle degenerate case (angle is ~0, ~180 or ~360)
            # Hide the angle arc and theta label as they are undefined/unstable
            self.angle_obj.set_stroke(opacity=0)
            self.theta.set_opacity(0)
            # The lines (self.line1, self.line2) are still updated above, so they keep moving.


class AnglesMoving(Scene):
    def construct(self):

        self.camera.background_color = INDIGO

        # Define parameters
        circle_radius = 1.5
        shift_distance = 3.0 # Distance to shift circles left/right
        initial_alpha = 0.001 # Start slightly off 0 to avoid initial degenerate angle

        # Create left path (shifted left)
        path_left = ParametricFunction(
            lambda t: np.array([
                circle_radius * np.cos(t) - shift_distance, # Shift x left
                circle_radius * np.sin(t),                  # y-coordinate
                0                                           # z-coordinate
            ]),
            t_range=[0, TAU],
            color=YELLOW_A,
            stroke_opacity=0.3
        )

        # Create right path (shifted right)
        path_right = ParametricFunction(
            lambda t: np.array([
                circle_radius * np.cos(t) + shift_distance, # Shift x right
                circle_radius * np.sin(t),                  # y-coordinate
                0                                           # z-coordinate
            ]),
            t_range=[0, TAU],
            color=RED_A, # Different color for distinction
            stroke_opacity=0.3
        )
        self.add(path_left, path_right)

        # Initial state for both angles
        initial_pos_left = path_left.point_from_proportion(initial_alpha)
        initial_pos_right = path_right.point_from_proportion(initial_alpha)
        initial_angle_value = initial_alpha * 360 * DEGREES

        # Create two instances of AngleGroup
        angle_group_left = AngleGroup(initial_pos_left, initial_angle_value, path_left)
        angle_group_right = AngleGroup(initial_pos_right, initial_angle_value, path_right)

        # Add both groups to the scene
        self.add(angle_group_left, angle_group_right)

        # Combined updater function for both groups
        def update_all_angles(mob, alpha):
            # mob is the VGroup containing both angle groups
            # We need to update each group individually using its own update method
            angle_group_left.update_components(alpha)
            angle_group_right.update_components(alpha)

        # Group the two angle groups for the updater
        # Note: We add the individual groups to the scene for display,
        # but use a temporary VGroup for the UpdateFromAlphaFunc target
        # if we don't want the updater group itself added to the scene.
        # Alternatively, apply the updater to each group separately if needed,
        # but a single updater is often cleaner.
        all_angle_groups = VGroup(angle_group_left, angle_group_right)

        # Create animation using the combined updater
        # The updater function modifies the objects directly,
        # so the target 'all_angle_groups' is just a handle.
        animation = UpdateFromAlphaFunc(all_angle_groups, update_all_angles)

        # Play the animation
        self.play(animation, run_time=15, rate_func=linear)

        # Wait for a moment
        self.wait(2)
