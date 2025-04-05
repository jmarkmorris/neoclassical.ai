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


class AnglesMoving(Scene):
    def construct(self):

        self.camera.background_color = INDIGO

        # Define parameters
        circle_radius = 1.5 * 0.5 * 0.9 * 0.9 * 0.9 # Make radius 50% smaller, then 10% smaller three times
        shift_distance_x = 3.0    # Increased Horizontal distance between columns
        shift_distance_y = 2.5    # Vertical distance between rows (adjust as needed)
        initial_alpha = 0.001     # Start slightly off 0 to avoid initial degenerate angle
        animation_duration = 15.0
        num_rows = 3
        num_cols = 4

        # Calculate the starting position for the grid (top-left)
        # Center the grid horizontally: total_width = (num_cols - 1) * shift_distance_x
        # Center the grid vertically: total_height = (num_rows - 1) * shift_distance_y
        start_x = - (num_cols - 1) * shift_distance_x / 2
        start_y = (num_rows - 1) * shift_distance_y / 2 - 0.3 # Shift grid down by 0.5, then up by 0.2

        # Define center points for the 3x4 grid using loops
        centers = []
        for r in range(num_rows):
            for c in range(num_cols):
                center_x = start_x + c * shift_distance_x
                base_center_y = start_y - r * shift_distance_y
                # Apply row-specific vertical shifts
                if r == 1: # Row 2 (0-indexed)
                    adjusted_center_y = base_center_y + 0.1
                elif r == 2: # Row 3 (0-indexed)
                    adjusted_center_y = base_center_y + 0.2
                else: # Row 1 (r=0) or any other rows
                    adjusted_center_y = base_center_y
                centers.append(np.array([center_x, adjusted_center_y, 0]))

        # Define colors for paths (ensure enough colors or allow cycling)
        path_colors = [
            YELLOW_A, GREEN_A, RED_A, BLUE_A,
            PURPLE_A, ORANGE, PINK, TEAL_A,
            GOLD_A, MAROON_A, LIGHT_GREY, WHITE
        ]

        paths = []
        angle_groups = []

        # Create paths and angle groups for each center point
        for i, center in enumerate(centers):
            path = ParametricFunction(
                lambda t, c=center: np.array([
                    circle_radius * np.cos(t) + c[0], # x-coordinate
                    circle_radius * np.sin(t) + c[1], # y-coordinate
                    c[2]                              # z-coordinate (remains 0)
                ]),
                t_range=[0, TAU],
                color=path_colors[i % len(path_colors)], # Cycle through colors
                stroke_opacity=0.3
            )
            paths.append(path)

            angle_group = AngleGroup(initial_alpha, path, duration=animation_duration)
            angle_groups.append(angle_group)

            # Add updater to the angle group
            angle_group.add_updater(lambda mob, dt: mob.update(dt))

        # Add all paths and angle groups to the scene
        self.add(*paths)
        self.add(*angle_groups)

        # Wait for the duration of the animation for the updaters to run
        self.wait(animation_duration)

        # Optional: Remove updaters from all angle groups
        for group in angle_groups:
            # Need to be careful removing lambda updaters; storing them might be safer.
            # However, for this simple case, clearing all updaters works.
            group.clear_updaters() # Simpler way to remove all updaters

        # Wait for a moment at the end
        self.wait(2)
