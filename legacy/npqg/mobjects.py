from manim import *
import numpy as np
import random

# Define a pool of distinct colors for random selection
RANDOM_COLOR_POOL = [
    RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, PINK, TEAL, MAROON, GOLD, WHITE, LIGHT_GRAY, GRAY, 
    BLUE_A, BLUE_B, BLUE_C, BLUE_D, BLUE_E, 
    GREEN_A, GREEN_B, GREEN_C, GREEN_D, GREEN_E, 
    RED_A, RED_B, RED_C, RED_D, RED_E, 
    YELLOW_A, YELLOW_B, YELLOW_C, YELLOW_D, YELLOW_E
]

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    norm = np.linalg.norm(vector)
    if norm == 0:
       return vector # Return zero vector if input is zero vector
    return vector / norm

def get_distinct_random_colors(n, pool=RANDOM_COLOR_POOL):
    """ Returns n distinct random colors from the pool. """
    if n > len(pool):
        print(f"Warning: Requested {n} distinct colors, but pool only has {len(pool)}. Returning duplicates.")
        # Allow duplicates if pool is too small
        return random.choices(pool, k=n)
    return random.sample(pool, n)

# Reusable Angle Group Class
class AngleGroup(VGroup):

    def __init__(self, initial_alpha, path, duration=1.0, colors="default", **kwargs):
        """
        Initializes the AngleGroup.
    
        Args:
            initial_alpha (float): Starting proportion along the path (0 to 1).
            path (ParametricCurve): The path the angle's vertex follows.
            duration (float): Time in seconds for the angle to traverse the path (0 to 360 degrees).
            colors (str or list): Color setting. Can be "default", "random", or a list/tuple
                                  of 5 specific colors for [line1, line2, arc, dot, theta].
            **kwargs: Additional arguments for VGroup.
        """
        super().__init__(**kwargs)

        self.path = path # Store the path for the updater
        self.initial_alpha = initial_alpha
        self.duration = duration
        self.speed = 1.0 / duration if duration > 0 else 0 # Speed as proportion per second
        self.current_alpha = initial_alpha
        self.is_updating = True # Flag to control the updater
        
        # Define base dimensions before they are used
        self.base_radius = 0.8  # Store the base radius for scaling calculations
        self.base_dot_radius = 0.07  # Store the base dot radius for scaling calculations
        
        # --- Determine Component Colors ---
        if colors == "random":
            # Request 4 colors, theta is always WHITE
            distinct_colors = get_distinct_random_colors(4)
            line1_color, line2_color, arc_color, dot_color = distinct_colors
        elif isinstance(colors, (list, tuple)) and len(colors) == 4:
            # Expect 4 colors if providing a list
            line1_color, line2_color, arc_color, dot_color = colors
        else: # Default colors
            line1_color = GREEN
            line2_color = ORANGE
            arc_color = BLUE_C
            dot_color = WHITE # Default dot color

        # Calculate initial state based on initial_alpha
        initial_position = path.point_from_proportion(initial_alpha)
        initial_angle_value = initial_alpha * 360 * DEGREES

        # Define points for the angle (relative to origin for calculation)
        A = np.array([1, 0, 0])
        O = np.array([0, 0, 0]) # Relative origin for angle calculation
        B = np.array([np.cos(initial_angle_value), np.sin(initial_angle_value), 0])

        # Calculate initial angle in degrees
        initial_angle_deg = int(round(initial_alpha * 360))
        # Store font size for updates
        self._theta_font_size = 16
        # Create initial text with degrees (forcing WHITE color)
        self.theta = Text(f"θ = {initial_angle_deg}°", color=WHITE, font_size=self._theta_font_size)

        # Initial theta position calculation
        # Use base_radius for initial positioning consistency
        base_offset_distance = self.base_radius + 0.5 # Base radius + buffer

        # Alternative theta positioning
        A_vec = A
        B_vec = B
        mid_vector = (A_vec + B_vec) / 2
        mid_vector_norm = np.linalg.norm(mid_vector)
        if mid_vector_norm > 1e-6:
            unit_mid_vector = mid_vector / mid_vector_norm
            # Position farther out using base offset distance
            theta_pos = initial_position + unit_mid_vector * base_offset_distance
        else:
            # Handle degenerate case
            # Use a default offset if mid_vector is zero (e.g., angle is 180 degrees)
            # A reasonable default might be perpendicular to A_vec
            default_offset_vector = np.array([-A_vec[1], A_vec[0], 0]) # Perpendicular in xy-plane
            if np.linalg.norm(default_offset_vector) < 1e-6: # If A_vec was along z? Fallback
                default_offset_vector = np.array([0, 1, 0])
            default_offset_vector = unit_vector(default_offset_vector)
            # Position farther out using base offset distance
            theta_pos = initial_position + default_offset_vector * base_offset_distance
        self.theta.move_to(theta_pos)

        # Create components relative to the initial position using determined colors
        self.line1 = Line(initial_position, initial_position + A, color=line1_color)
        self.line2 = Line(initial_position, initial_position + B, color=line2_color)
        # Ensure fill opacity is 0 from the start
        self.angle_obj = Angle(self.line1, self.line2, radius=self.base_radius, color=arc_color, 
                              dot=True, dot_radius=self.base_dot_radius, dot_distance=0, fill_opacity=0)
        # Explicitly set the dot color after creation
        if hasattr(self.angle_obj, 'dot') and self.angle_obj.dot is not None:
            self.angle_obj.dot.set_color(dot_color)

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

    def set_color(self, line1_color=None, line2_color=None, arc_color=None, dot_color=None):
        """
        Sets the color of individual components of the AngleGroup.
        Any component whose color is not specified will retain its current color.
        The theta label color is always WHITE and cannot be changed via this method.
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
    
                # --- Update Theta Text ---
                current_degrees = int(round(actual_angle_deg))
                new_theta_string = f"θ = {current_degrees}°"
                
                # Only update the Text mobject if the string content has changed
                if not hasattr(self.theta, 'text') or self.theta.text != new_theta_string:
                    # Create a new Text object with the updated string and original style
                    new_theta_text = Text(
                        new_theta_string,
                        color=WHITE, # Keep original color
                        font_size=self._theta_font_size # Keep original font size
                    )
                    # Use become to replace the old text object with the new one
                    self.theta.become(new_theta_text)
                # --- End Update Theta Text ---
                
                # Position the theta label only if not degenerate
                # Calculate offset: scaled base radius + fixed buffer
                theta_offset_distance = self.base_radius * scale_factor + 0.5 # Adjusted buffer

                # Calculate the bisector vector (using unscaled vectors for direction)
                bisector = A_vec + B_vec
                bisector_norm = np.linalg.norm(bisector)

                if bisector_norm > 1e-6:
                    # Normalize the bisector
                    unit_bisector = bisector / bisector_norm

                    # Flip the bisector for angles > 180°
                    if cross_product < 0:
                        unit_bisector = -unit_bisector

                    # Position theta along the bisector using the calculated offset distance
                    theta_pos = position + unit_bisector * theta_offset_distance
                    self.theta.move_to(theta_pos)
                else:
                    # Handle degenerate case (bisector is zero) for theta positioning
                    # Use a default offset if bisector is zero (e.g., angle is 180 degrees)
                    # A reasonable default might be perpendicular to A_vec
                    default_offset_vector = np.array([-A_vec[1], A_vec[0], 0]) # Perpendicular in xy-plane
                    if np.linalg.norm(default_offset_vector) < 1e-6: # If A_vec was along z? Fallback
                         default_offset_vector = np.array([0, 1, 0])
                    default_offset_vector = unit_vector(default_offset_vector)
                    theta_pos = position + default_offset_vector * theta_offset_distance
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
