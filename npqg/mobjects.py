from manim import *
import numpy as np

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

        # --- Scaling State Variables ---
        self._is_scaling = False          # Is a scaling animation active?
        self._scale_target = 1.0          # Target scale factor (relative to initial size)
        self._scale_duration = 0.0        # Duration of the scaling animation
        self._scale_elapsed_time = 0.0    # Time elapsed in the current scaling animation
        self._scale_start_value = 1.0     # Scale factor when the animation started
        self._current_scale_factor = 1.0  # Tracks the current cumulative scale factor applied

        # Initialize visuals to the starting state
        self._update_visuals(self.initial_alpha)

    # --- Helper methods for scaling ---
    def _get_current_scale_factor(self):
        """Returns the tracked current scale factor."""
        return self._current_scale_factor

    def _set_scale_factor(self, target_factor):
        """
        Applies scaling to reach the target_factor from the current factor.
        Updates the internal tracking variable.
        """
        if self._current_scale_factor == 0: # Avoid division by zero if already scaled to 0
             if target_factor == 0:
                 return # Already at target scale 0
             else:
                 # Cannot scale up from 0 using a multiplier.
                 # This case is tricky. For simplicity, let's assume we don't scale up from exactly 0.
                 # A more robust solution might involve storing initial size and scaling absolutely.
                 print("Warning: Cannot scale up from scale factor 0.")
                 return

        scale_multiplier = target_factor / self._current_scale_factor
        # print(f"DEBUG: _set_scale_factor - Target: {target_factor}, Current: {self._current_scale_factor}, Multiplier: {scale_multiplier}") # DEBUG - Removed
        self.scale(scale_multiplier) # Manim's scale method multiplies current size
        self._current_scale_factor = target_factor
        # print(f"DEBUG: _set_scale_factor - Scale applied. New _current_scale_factor: {self._current_scale_factor}") # DEBUG - Removed

    # --- Public method to trigger scaling ---
    # Duration is now the second positional argument
    def dynamic_scale(self, target_scale, duration):
        """
        Starts an animation to scale the AngleGroup to a target scale factor
        over a specified duration using the updater.

        Args:
            target_scale (float): The final scale factor (e.g., 1.0 is original size,
                                  0.5 is half size, 2.0 is double size).
            duration (float): The time in seconds the scaling animation should take.
        """
        if duration <= 0:
            # Apply instantly if duration is zero or negative
            self._set_scale_factor(target_scale)
            self._is_scaling = False
        else:
            self._scale_target = target_scale
            self._scale_duration = duration
            self._scale_elapsed_time = 0.0
            self._scale_start_value = self._get_current_scale_factor() # Start from current scale
            self._is_scaling = True # Activate scaling in the updater
            # print(f"DEBUG: dynamic_scale called. Target: {self._scale_target}, Duration: {self._scale_duration}, Start Scale: {self._scale_start_value}") # DEBUG - Removed

    def set_color(self, line1_color=None, line2_color=None, arc_color=None, dot_color=None, theta_color=None):
        """
        Sets the color of individual components of the AngleGroup.
        Any component whose color is not specified will retain its current color.

        Args:
            line1_color (Optional[str or Color]): Color for the first line.
            line2_color (Optional[str or Color]): Color for the second line.
            arc_color (Optional[str or Color]): Color for the angle arc.
            dot_color (Optional[str or Color]): Color for the angle dot.
            theta_color (Optional[str or Color]): Color for the theta label.
        """
        if line1_color is not None:
            self.line1.set_color(line1_color)
        if line2_color is not None:
            self.line2.set_color(line2_color)
        if arc_color is not None:
            # The main color of Angle is the arc color
            self.angle_obj.set_color(arc_color)
        if dot_color is not None and hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
            # The dot is a submobject of the Angle
            self.angle_obj.dot.set_color(dot_color)
        if theta_color is not None:
            self.theta.set_color(theta_color)
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
                # Preserve the existing colors of the arc and dot
                current_arc_color = self.angle_obj.get_color()
                current_dot_color = self.angle_obj.dot.get_color() if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None else WHITE # Default if no dot

                # Use a temporary Angle with the preserved colors
                temp_angle = Angle(self.line1, self.line2, radius=0.6, color=current_arc_color, dot=True, dot_radius=0.07, dot_distance=0, fill_opacity=0)
                # Set the dot color explicitly on the temporary angle's dot before 'become'
                if hasattr(temp_angle, 'dot') and temp_angle.dot is not None:
                    temp_angle.dot.set_color(current_dot_color)

                self.angle_obj.become(temp_angle)
                # Explicitly set stroke opacity, keep fill opacity at 0
                self.angle_obj.set_stroke(opacity=1)
                # Re-apply dot color just in case 'become' didn't transfer it perfectly
                if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
                     self.angle_obj.dot.set_color(current_dot_color)

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

    # Accept 'recursive' as the third positional argument passed by Manim's internal update loop
    def update(self, dt, recursive=True, **kwargs):
        """Standard Manim updater function."""
        # We don't explicitly use 'recursive' here, but accept it positionally.
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

        # --- Handle Dynamic Scaling ---
        if self._is_scaling:
            self._scale_elapsed_time += dt

            if self._scale_elapsed_time >= self._scale_duration:
                # Animation finished, snap to target and stop scaling
                self._set_scale_factor(self._scale_target)
                self._is_scaling = False
            else:
                # Calculate linear progress (0 to 1)
                progress = self._scale_elapsed_time / self._scale_duration
                # Interpolate the scale factor linearly
                interpolated_scale = self._scale_start_value + (self._scale_target - self._scale_start_value) * progress
                # Apply the interpolated scale
                self._set_scale_factor(interpolated_scale)
