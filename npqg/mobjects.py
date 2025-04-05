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
        
        This scaling keeps the apex of the angle fixed and scales:
        - The length of both lines
        - The radius of the angle arc
        - The position of the theta label
        """
        if self._current_scale_factor == 0: # Avoid division by zero if already scaled to 0
             if target_factor == 0:
                 return # Already at target scale 0
             else:
                 # Cannot scale up from 0 using a multiplier.
                 print("Warning: Cannot scale up from scale factor 0.")
                 return

        scale_multiplier = target_factor / self._current_scale_factor
        
        # Get current position (apex of the angle)
        current_position = self.line1.get_start()
        
        # Scale the lines while keeping their start points fixed
        line1_end = current_position + (self.line1.get_end() - current_position) * scale_multiplier
        line2_end = current_position + (self.line2.get_end() - current_position) * scale_multiplier
        
        self.line1.put_start_and_end_on(current_position, line1_end)
        self.line2.put_start_and_end_on(current_position, line2_end)
        
        # Scale the angle arc radius
        current_arc_color = self.angle_obj.get_color()
        current_dot_color = self.angle_obj.dot.get_color() if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None else WHITE
        
        # Create a new angle with scaled radius
        new_radius = 0.6 * scale_multiplier
        temp_angle = Angle(self.line1, self.line2, radius=new_radius, color=current_arc_color, 
                           dot=True, dot_radius=0.07 * scale_multiplier, dot_distance=0, fill_opacity=0)
        
        if hasattr(temp_angle, 'dot') and temp_angle.dot is not None:
            temp_angle.dot.set_color(current_dot_color)
            
        self.angle_obj.become(temp_angle)
        self.angle_obj.set_stroke(opacity=1)
        
        if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
            self.angle_obj.dot.set_color(current_dot_color)
        
        # Reposition theta label based on the new scale
        angle_value = self.current_alpha * 360 * DEGREES
        A_vec = np.array([1, 0, 0])
        B_vec = np.array([np.cos(angle_value), np.sin(angle_value), 0])
        
        mid_vector = (A_vec + B_vec) / 2
        mid_vector_norm = np.linalg.norm(mid_vector)
        
        if mid_vector_norm > 1e-6:
            unit_mid_vector = mid_vector / mid_vector_norm
            
            # Check if angle is greater than 180 degrees using cross product
            cross_product = np.cross(A_vec, B_vec)[2]  # z-component of cross product
            if cross_product < 0:  # Second line is clockwise from first line (angle > 180)
                unit_mid_vector = -unit_mid_vector
                
            # Scale the distance of theta from the apex
            line_length = 1.0 * scale_multiplier
            theta_pos = current_position + unit_mid_vector * 1.1 * line_length
            self.theta.move_to(theta_pos)
            # Do not scale the theta text size
        
        # Update the current scale factor
        self._current_scale_factor = target_factor

    # --- Public method to trigger scaling ---
    def dynamic_scale(self, target_scale, duration):
        """
        Starts an animation to scale the AngleGroup to a target scale factor
        over a specified duration using the updater.

        The scaling happens incrementally on each frame update, with the amount
        of change per frame determined by:
        1. The total change in scale (target_scale - current_scale)
        2. The duration of the animation
        3. The easing function applied to the progress

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
            # Store parameters for the scaling animation
            self._scale_target = target_scale
            self._scale_duration = duration
            self._scale_elapsed_time = 0.0
            self._scale_start_value = self._get_current_scale_factor() # Start from current scale
            self._is_scaling = True # Activate scaling in the updater

    def set_color(self, line1_color=None, line2_color=None, arc_color=None, dot_color=None, theta_color=None):
        """
        Sets the color of individual components of the AngleGroup.
        Any component whose color is not specified will retain its current color.
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
        
        # Calculate the actual angle between vectors (in degrees for debugging)
        dot_product = np.dot(A_vec, B_vec)
        cross_product = np.cross(A_vec, B_vec)[2]  # z-component
        actual_angle_deg = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))
        
        # Determine the correct sign based on cross product
        if cross_product < 0:
            actual_angle_deg = 360 - actual_angle_deg

        # Apply current scale factor to the line lengths
        scale_factor = self._current_scale_factor
        scaled_A_vec = A_vec * scale_factor
        scaled_B_vec = B_vec * scale_factor

        # Update lines with scaled vectors
        self.line1.put_start_and_end_on(position, position + scaled_A_vec)
        self.line2.put_start_and_end_on(position, position + scaled_B_vec)

        # Check for parallel/anti-parallel lines (angle near 0, 180, 360 deg)
        # Use a small tolerance (atol) for floating point comparisons
        # Use the actual calculated angle rather than the alpha-based angle
        is_degenerate = np.isclose(actual_angle_deg % 180, 0, atol=1e-6)

        if not is_degenerate:
            # Update angle object only if lines are not parallel/anti-parallel
            try:
                # Ensure new angle also has no fill
                # Preserve the existing colors of the arc and dot
                current_arc_color = self.angle_obj.get_color()
                current_dot_color = self.angle_obj.dot.get_color() if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None else WHITE # Default if no dot

                # Use a temporary Angle with the preserved colors and scaled radius
                scaled_radius = 0.6 * self._current_scale_factor
                scaled_dot_radius = 0.07 * self._current_scale_factor
                temp_angle = Angle(self.line1, self.line2, radius=scaled_radius, color=current_arc_color, 
                                  dot=True, dot_radius=scaled_dot_radius, dot_distance=0, fill_opacity=0)
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
            # Apply current scale factor to the line length
            line_length = 1.0 * self._current_scale_factor # Scale the unit vector

            # Alternative theta positioning
            mid_vector = (A_vec + B_vec) / 2
            mid_vector_norm = np.linalg.norm(mid_vector)
            if mid_vector_norm > 1e-6:
                unit_mid_vector = mid_vector / mid_vector_norm

                # Check if angle is greater than 180 degrees (PI radians)
                # Use the cross product to determine which side of the first line the second line is on
                cross_product = np.cross(A_vec, B_vec)[2]  # z-component of cross product
                if cross_product < 0:  # Second line is clockwise from first line (angle > 180)
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
            # Increment elapsed time by the frame delta time
            self._scale_elapsed_time += dt

            if self._scale_elapsed_time >= self._scale_duration:
                # Animation finished, snap to target and stop scaling
                self._set_scale_factor(self._scale_target)
                self._is_scaling = False
            else:
                # Calculate progress (0 to 1) with smooth easing
                linear_progress = self._scale_elapsed_time / self._scale_duration
                
                # Apply smooth easing function (ease in-out)
                # This creates a more natural, less jumpy animation
                if linear_progress < 0.5:
                    # Ease in: slow start, accelerate
                    progress = 2 * linear_progress * linear_progress
                else:
                    # Ease out: decelerate to end
                    progress = 1 - pow(-2 * linear_progress + 2, 2) / 2
                
                # Interpolate the scale factor with the eased progress
                # This ensures a smooth transition from start to target scale
                interpolated_scale = self._scale_start_value + (self._scale_target - self._scale_start_value) * progress
                
                # Apply the interpolated scale for this frame
                self._set_scale_factor(interpolated_scale)
