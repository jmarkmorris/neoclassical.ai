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
        angle = Angle(line1, line2, radius=0.8, color=BLUE_C, dot=True, dot_radius=0.07, dot_distance=0)
        
        # Create theta label
        theta = MathTex(r"\theta", color=WHITE).scale(0.6)

        # Initial theta position calculation
        line_length = np.linalg.norm(A - O)
        arc_center = position  # Initial position is at the origin
        theta_pos = angle.point_from_proportion(0.5)
        theta_pos = arc_center + unit_vector(theta_pos - arc_center) * 1.1 * line_length

        theta.move_to(theta_pos)
        
        self.angle_group = VGroup(line1, line2, angle, theta)
        self.add(self.angle_group)

        # Animate the angle moving along the path
        def update_angle_position(mob, alpha):
            position = path.point_from_proportion(alpha)
            
            # Update the angle's lines
            angle_value = alpha * 360 * DEGREES  # Rotate 360 degrees over the animation
            
            # Define new points for the lines relative to the origin
            A = np.array([1, 0, 0])
            B = np.array([np.cos(angle_value), np.sin(angle_value), 0])
            O = np.array([0, 0, 0])  # Origin

            # Create new lines with the origin at the path position
            line1 = Line(position, position + A, color=GREEN)
            line2 = Line(position, position + B, color=ORANGE)
            
            # Check if lines are parallel
            if not np.isclose(np.linalg.norm(np.cross(A - O, B - O)), 0):
                # Update the angle with the new lines
                new_angle = Angle(line1, line2, color=BLUE_C, radius=0.8, dot=True, dot_radius=0.07, dot_distance=0)
                
                # Calculate theta position
                theta_pos = new_angle.point_from_proportion(0.5)
        
                # Get line length (assuming both lines have same length)
                line_length = np.linalg.norm(A - O)
        
                # Get a point outside the arc, at double the line length distance
                arc_center = new_angle.get_center()
                
                theta_pos = arc_center + unit_vector(theta_pos - arc_center) * 1.1 * line_length
        
                theta.move_to(theta_pos)
        
                mob.become(VGroup(line1, line2, new_angle, theta))
            else:
                # If lines are parallel, keep the previous state
                pass

        # Create animation to move the angle along the path
        animation = UpdateFromAlphaFunc(self.angle_group, update_angle_position)

        # Create animation to move the angle along the path
        animation = UpdateFromAlphaFunc(self.angle_group, update_angle_position)

        # Play the animation
        self.play(animation, run_time=15, rate_func=linear)

        # Wait for a moment
        self.wait(2)
