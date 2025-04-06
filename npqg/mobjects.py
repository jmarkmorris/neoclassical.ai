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
        self.base_radius = 0.8  # Store the base radius for scaling calculations
        self.base_dot_radius = 0.07  # Store the base dot radius for scaling calculations
        self.angle_obj = Angle(self.line1, self.line2, radius=self.base_radius, color=BLUE_C, 
                              dot=True, dot_radius=self.base_dot_radius, dot_distance=0, fill_opacity=0)
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
        Updates the internal tracking variable and refreshes the visuals.
        
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

        # Update the scale factor first
        self._current_scale_factor = target_factor
        
        # Then update the visuals with the current alpha
        # This ensures consistent scaling behavior between direct scaling and animation
        # All visual updates, including theta positioning, are handled in _update_visuals
        self._update_visuals(self.current_alpha)

    # --- Public method to trigger scaling ---
    def dynamic_scale(self, start_time, end_time, target_scale):
        """
        Schedule a scaling operation with precise start and end times.
        
        Args:
            start_time (float): The time at which scaling should begin
            end_time (float): The time at which scaling should complete
            target_scale (float): The final scale factor to reach
        """
        # If no scaling operations exist, initialize the queue
        if not hasattr(self, '_scale_queue'):
            self._scale_queue = []
        
        # Check for conflicts with existing scaling operations
        for existing_scale in self._scale_queue:
            if not (end_time <= existing_scale['start_time'] or 
                    start_time >= existing_scale['end_time']):
                print(f"Warning: Scaling operation from {start_time} to {end_time} "
                      f"conflicts with existing operation from "
                      f"{existing_scale['start_time']} to {existing_scale['end_time']}. "
                      "Operation ignored.")
                return
        
        # Add the new scaling operation to the queue
        new_scale_op = {
            'start_time': start_time,
            'end_time': end_time,
            'start_scale': self._current_scale_factor,
            'target_scale': target_scale,
            'duration': end_time - start_time
        }
        self._scale_queue.append(new_scale_op)
        
        # Sort the queue by start time to ensure proper order of operations
        self._scale_queue.sort(key=lambda x: x['start_time'])
            
    def pause_animation(self):
        """
        Pauses both the angle rotation and scaling animations.
        The current state is preserved so animations can be resumed later.
        """
        self.is_updating = False
        self._is_scaling = False
        
    def resume_animation(self):
        """
        Resumes both the angle rotation and scaling animations from where they were paused.
        If scaling was in progress when paused, it will continue from its current progress.
        """
        self.is_updating = True
        
        # Only resume scaling if we haven't reached the target yet
        if self._scale_elapsed_time < self._scale_duration and abs(self._current_scale_factor - self._scale_target) > 1e-6:
            self._is_scaling = True

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
        # Store the current alpha for other methods to use
        self.current_alpha = np.clip(alpha, 0, 1)
        
        # Get position on the path
        position = self.path.point_from_proportion(self.current_alpha)
        angle_value = self.current_alpha * 360 * DEGREES

        # Define new vectors relative to origin (for angle calculation)
        A_vec = np.array([1, 0, 0])
        B_vec = np.array([np.cos(angle_value), np.sin(angle_value), 0])
        
        # Use atan2 for more robust angle calculation
        # This handles the full 360-degree range correctly
        angle_in_radians = np.arctan2(B_vec[1], B_vec[0])
        if angle_in_radians < 0:
            angle_in_radians += 2 * np.pi  # Convert to [0, 2π] range
        
        actual_angle_deg = np.degrees(angle_in_radians)
        
        # Calculate cross product for later use with the bisector
        cross_product = np.cross(A_vec, B_vec)[2]  # z-component

        # Apply current scale factor to the line lengths
        scale_factor = self._current_scale_factor
        scaled_A_vec = A_vec * scale_factor
        scaled_B_vec = B_vec * scale_factor

        # Update lines with scaled vectors
        self.line1.put_start_and_end_on(position, position + scaled_A_vec)
        self.line2.put_start_and_end_on(position, position + scaled_B_vec)

        # Check for parallel/anti-parallel lines (angle near 0, 180, 360 deg)
        # Use a scale-aware tolerance for floating point comparisons
        # Adjust tolerance based on scale factor to handle scaled angles better
        tolerance = 1e-6 * max(1.0, self._current_scale_factor)
        # Consider 0 and 180 degenerate, but allow 360 to show the full arc
        is_degenerate = (np.isclose(actual_angle_deg, 0, atol=tolerance) or
                         np.isclose(actual_angle_deg, 180, atol=tolerance))
        is_full_circle = np.isclose(actual_angle_deg, 360, atol=tolerance)

        # Handle degenerate angles (0, 180) first by hiding components
        if is_degenerate and not is_full_circle: # Exclude the 360 case from hiding
            self.angle_obj.set_stroke(opacity=0)
            if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
                self.angle_obj.dot.set_opacity(0)
            self.theta.set_opacity(0)
        else:
            # If not degenerate, update the angle object and theta
            try:
                # Preserve the existing colors of the arc and dot
                current_arc_color = self.angle_obj.get_color()
                current_dot_color = self.angle_obj.dot.get_color() if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None else WHITE

                # Create a new angle with the current scale factor applied
                scaled_radius = self.base_radius * scale_factor
                scaled_dot_radius = self.base_dot_radius * scale_factor

                # Create a new angle with the scaled dimensions
                temp_angle = Angle(
                    self.line1, self.line2,
                    radius=scaled_radius,
                    color=current_arc_color,
                    dot=True,
                    dot_radius=scaled_dot_radius,
                    dot_distance=0,
                    fill_opacity=0
                )

                # Set the dot color explicitly
                if hasattr(temp_angle, 'dot') and temp_angle.dot is not None:
                    temp_angle.dot.set_color(current_dot_color)

                # Update the angle object
                self.angle_obj.become(temp_angle)

                # Set visibility to 1 (since it's not degenerate)
                self.angle_obj.set_stroke(opacity=1)
                if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
                    self.angle_obj.dot.set_color(current_dot_color) # Re-apply color after become
                    self.angle_obj.dot.set_opacity(1)

                # Position the theta label only if not degenerate
                line_length = 1.0 * scale_factor  # Scale the unit vector

                # Calculate the bisector vector
                bisector = A_vec + B_vec
                bisector_norm = np.linalg.norm(bisector)

                if bisector_norm > 1e-6:
                    # Normalize the bisector
                    unit_bisector = bisector / bisector_norm

                    # Flip the bisector for angles > 180°
                    if cross_product < 0:
                        unit_bisector = -unit_bisector

                    # Position theta along the bisector
                    theta_pos = position + unit_bisector * 1.1 * line_length
                    self.theta.move_to(theta_pos)
                else:
                    # Handle degenerate case (bisector is zero) for theta positioning
                    default_offset_vector = A_vec / np.linalg.norm(A_vec)
                    theta_pos = position + default_offset_vector * 1.1 * line_length
                    self.theta.move_to(theta_pos)

                # Set theta visibility to 1, unless it's a full circle (position is ambiguous)
                self.theta.set_opacity(0 if is_full_circle else 1)

            except ValueError:
                # If angle creation fails even when not initially degenerate or full circle, hide components
                self.angle_obj.set_stroke(opacity=0)
                if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
                    self.angle_obj.dot.set_opacity(0)
                self.theta.set_opacity(0)

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
            pass # Keep showing the final state if clamped

        # Track the current time of the animation
        if not hasattr(self, '_current_animation_time'):
            self._current_animation_time = 0.0
        
        self._current_animation_time += dt
        
        # Process scaling queue
        if hasattr(self, '_scale_queue') and self._scale_queue:
            current_op = self._scale_queue[0]
            
            # Check if it's time to start this scaling operation
            if self._current_animation_time >= current_op['start_time']:
                # If we're within the scaling window
                if self._current_animation_time <= current_op['end_time']:
                    # Calculate progress
                    progress = (self._current_animation_time - current_op['start_time']) / current_op['duration']
                    
                    # Apply smooth interpolation
                    interpolated_scale = (
                        current_op['start_scale'] + 
                        (current_op['target_scale'] - current_op['start_scale']) * progress
                    )
                    
                    self._set_scale_factor(interpolated_scale)
                
                # If we've completed this scaling operation
                if self._current_animation_time >= current_op['end_time']:
                    # Ensure we reach the exact target scale
                    self._set_scale_factor(current_op['target_scale'])
                    
                    # Remove this operation from the queue
                    self._scale_queue.pop(0)
