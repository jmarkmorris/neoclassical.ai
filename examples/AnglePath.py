from manim import *
import numpy as np

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
WHITE = "#FFFFFF"

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

class AngleNew(Scene):
    def construct(self):

        self.camera.background_color = INDIGO

        # Create a complex path for the angle to follow
        path = ParametricFunction(
            lambda t: np.array([
                3 * np.sin(t * 2),  # x-coordinate
                2 * np.cos(t * 3),  # y-coordinate
                0                   # z-coordinate
            ]),
            t_range=[0, TAU],
            color=YELLOW_A,
            stroke_opacity=0.3     # Subtle path visualization
        )
        self.add(path)

        alpha = 0.001  # Initial alpha value for the angle
        position = path.point_from_proportion(alpha)
        angle_value = alpha * 360 * DEGREES  # Rotate 360 degrees over the animation

        # Define points for the angle
        A = np.array([1, 0, 0])
        O = np.array([0, 0, 0])
        B = np.array([np.cos(angle_value), np.sin(angle_value), 0])

        line1 = Line(position, position + A, color=GREEN)
        line2 = Line(position, position + B, color=ORANGE)
        
        # Create the angle object
        # Store components as attributes
        self.line1 = Line(position, position + A, color=GREEN)
        self.line2 = Line(position, position + B, color=ORANGE)
        # Ensure fill opacity is 0 from the start
        self.angle_obj = Angle(self.line1, self.line2, radius=0.8, color=BLUE_C, dot=True, dot_radius=0.07, dot_distance=0, fill_opacity=0)
        self.theta = MathTex(r"\theta", color=WHITE).scale(0.6)

        # Initial theta position calculation
        line_length = np.linalg.norm(A - O) # Norm is 1
        arc_center = self.angle_obj.get_center()
        theta_pos_on_arc = self.angle_obj.point_from_proportion(0.5)
        direction_vector = theta_pos_on_arc - arc_center
        direction_norm = np.linalg.norm(direction_vector)
        if direction_norm > 1e-6:
            unit_dir_vec = direction_vector / direction_norm
            theta_pos = arc_center + unit_dir_vec * 1.1 * line_length
        else: # Handle initial degenerate case if alpha starts near 0/1
            default_offset_vector = A / np.linalg.norm(A)
            theta_pos = position + default_offset_vector * 1.1 * line_length
        self.theta.move_to(theta_pos)

        # Create radial line
        self.radial_line = Line(position, theta_pos_on_arc, color=WHITE, stroke_width=1)

        self.angle_group = VGroup(self.line1, self.line2, self.angle_obj, self.theta, self.radial_line)
        self.add(self.angle_group)

        # Updater function to modify components in place
        def update_angle_components(mob, alpha):
            position = path.point_from_proportion(alpha)
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
                    new_angle = Angle(self.line1, self.line2, radius=0.8, color=BLUE_C, dot=True, dot_radius=0.07, dot_distance=0, fill_opacity=0)
                    self.angle_obj.become(new_angle)
                    # Explicitly set stroke opacity, keep fill opacity at 0
                    self.angle_obj.set_stroke(opacity=1)
                except ValueError:
                    # This should ideally not happen due to the is_degenerate check, but as a safeguard:
                    is_degenerate = True # Treat as degenerate if Angle() fails

            # Check is_degenerate *again* because the try-except might have changed it
            if not is_degenerate:
                # Calculate theta position safely only if angle is valid
                theta_pos_on_arc = self.angle_obj.point_from_proportion(0.5) # Use updated angle_obj
                arc_center = self.angle_obj.get_center() # Center of the *updated* angle
                direction_vector = theta_pos_on_arc - arc_center
                direction_norm = np.linalg.norm(direction_vector)

                line_length = 1.0 # Since A_vec is unit vector

                if direction_norm > 1e-6:
                    # Normal case for theta positioning
                    unit_dir_vec = direction_vector / direction_norm
                    theta_pos = arc_center + unit_dir_vec * 1.1 * line_length
                    self.theta.move_to(theta_pos)
                    self.theta.set_opacity(1)
                    # angle_obj opacity was set to 1 in the try block above
                else:
                    # Handle degenerate direction_vector (should be rare if angle isn't degenerate)
                    # Place theta along the first line's direction as a fallback
                    default_offset_vector = A_vec / np.linalg.norm(A_vec) # Unit vector along A
                    theta_pos = position + default_offset_vector * 1.1 * line_length
                    self.theta.move_to(theta_pos)
                    self.theta.set_opacity(1) # Keep theta visible
                    # angle_obj opacity was set to 1 in the try block above
            else:
                # Handle degenerate case (angle is ~0, ~180 or ~360)
                # Hide the angle arc and theta label as they are undefined/unstable
                # Use set_stroke for the angle object
                self.angle_obj.set_stroke(opacity=0)
                self.theta.set_opacity(0) # Keep using set_opacity for MathTex
                # The lines (self.line1, self.line2) are still updated above, so they keep moving.

            # Update radial line
            theta_pos_on_arc = self.angle_obj.point_from_proportion(0.5)
            radial_line_end = position + 2 * (theta_pos_on_arc - position)
            self.radial_line.put_start_and_end_on(position, radial_line_end)

        # Create animation using the new updater
        animation = UpdateFromAlphaFunc(self.angle_group, update_angle_components)

        # Play the animation
        self.play(animation, run_time=15, rate_func=linear)

        # Wait for a moment
        self.wait(2)
