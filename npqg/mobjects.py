from manim import *
import numpy as np

# Define colors if they are specifically needed by AngleGroup or its helpers
# If they are only used by the Scene, they can stay in AngleClass.py
# INDIGO = "#4B0082" # Not used by AngleGroup directly
# ELECTRIC_PURPLE = "#8F00FF" # Not used by AngleGroup directly
WHITE = "#FFFFFF" # Used by MathTex in AngleGroup

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    norm = np.linalg.norm(vector)
    if norm == 0:
       return vector # Return zero vector if input is zero vector
    return vector / norm

# Reusable Angle Group Class
class AngleGroup(VGroup):
    def __init__(self, initial_alpha, path, duration=1.0, **kwargs):
        super().__init__(**kwargs)
        self.path = path # Store the path for the updater
        self.initial_alpha = initial_alpha
        self.duration = duration
        self.speed = 1.0 / duration if duration > 0 else 0 # Speed as proportion per second
        self.current_alpha = initial_alpha
        self.is_updating = True # Flag to control the updater

        # Calculate initial state based on initial_alpha
        initial_position = path.point_from_proportion(initial_alpha)
        initial_angle_value = initial_alpha * 360 * DEGREES

        # Define points for the angle (relative to origin for calculation)
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

        # Initialize visuals to the starting state
        self._update_visuals(self.initial_alpha)

    def set_color(self, color):
        """Sets the color of all components of the AngleGroup."""
        self.line1.set_color(color)
        self.line2.set_color(color)
        self.angle_obj.set_color(color)
        self.theta.set_color(color)
        # Return self to allow chaining if needed
        return self

    # Renamed from update_components
    def _update_visuals(self, alpha):
        """Updates the visual components based on the given alpha."""
        # Clamp alpha to avoid errors with point_from_proportion if it goes outside [0, 1]
        clamped_alpha = np.clip(alpha, 0, 1)
        position = self.path.point_from_proportion(clamped_alpha)
        angle_value = clamped_alpha * 360 * DEGREES

        # Define new vectors relative to origin (for angle calculation)
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
                temp_angle = Angle(self.line1, self.line2, radius=0.6, color=BLUE_C, dot=True, dot_radius=0.07, dot_distance=0, fill_opacity=0)
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

    def update(self, dt):
        """Standard Manim updater function."""
        if not self.is_updating:
            return

        if self.current_alpha < 1.0:
            self.current_alpha += self.speed * dt
            # Ensure alpha doesn't exceed 1 due to dt fluctuations
            self.current_alpha = min(self.current_alpha, 1.0)
            self._update_visuals(self.current_alpha)
        else:
            # Optionally stop updating once alpha reaches 1
            # self.is_updating = False
            # Or handle looping if desired
            # self.current_alpha = self.current_alpha % 1.0 # Loop
            pass # Keep showing the final state if clamped
