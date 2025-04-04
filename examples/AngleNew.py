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
        # Set background color
        try:
            self.camera.background_color = INDIGO
        except NameError:
            print("Warning: INDIGO color not defined, using default background.")
            pass
        # Define points for the angle
        A = np.array([1, 0, 0])
        O = np.array([0, 0, 0])
        B = np.array([1, 1, 0])

        # Define new lines
        line1 = Line(O, A, color=TEAL_A)
        line2 = Line(O, B, color=PINK)
        
        # Create the angle object
        angle = Angle(line1, line2, radius=0.5, color=WHITE)
        
        # Create theta label
        theta = MathTex(r"\theta", color=WHITE).scale(0.8)
        
        self.angle_group = VGroup(line1, line2, angle, theta)
        self.add(self.angle_group)
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

        # Animate the angle moving along the path
        def update_angle_position(mob, alpha):
            position = path.point_from_proportion(alpha)
            
            # Update the angle's lines
            angle_value = alpha * 360 * DEGREES  # Rotate 360 degrees over the animation
            
            # Define new points for the lines
            A = np.array([1, 0, 0])
            B = np.array([np.cos(angle_value), np.sin(angle_value), 0])
            O = np.array([0, 0, 0])
            
            # Define new points for the lines relative to the origin
            A = np.array([1, 0, 0])
            B = np.array([np.cos(angle_value), np.sin(angle_value), 0])
            O = np.array([0, 0, 0])  # Origin

            # Create new lines with the origin at the path position
            line1 = Line(position, position + A, color=TEAL_A)
            line2 = Line(position, position + B, color=PINK)
            
            # Check if lines are parallel
            if not np.isclose(np.linalg.norm(np.cross(A - O, B - O)), 0):
                # Update the angle with the new lines
                new_angle = Angle(line1, line2, color=WHITE, radius=0.5)
                
                # Calculate theta position
                theta_pos = new_angle.point_from_proportion(0.5)
        
                # Get line length (assuming both lines have same length)
                line_length = np.linalg.norm(A - O)
        
                # Get a point outside the arc, at double the line length distance
                arc_center = new_angle.get_center()
                
                # Reduce the radius by 30%
                theta_pos = arc_center + unit_vector(theta_pos - arc_center) * 2 * line_length * 0.7
        
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
