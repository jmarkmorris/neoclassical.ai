from manim import *
import numpy as np
from tools import INDIGO  # Assuming tools.py exists with INDIGO defined
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

        # Create the angle object
        angle = Angle(line1=Line(O,A), line2=Line(O,B), radius=0.5, color=YELLOW)
        self.add(angle)
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
            mob.move_to(position)
            
            # Update the angle's lines
            angle_value = alpha * 360 * DEGREES  # Rotate 360 degrees over the animation
            
            # Define new points for the lines
            A = np.array([1, 0, 0])
            B = np.array([np.cos(angle_value), np.sin(angle_value), 0])
            O = np.array([0, 0, 0])
            
            # Create new lines
            line1 = Line(O, A)
            line2 = Line(O, B)

            # Check if lines are parallel
            if not np.isclose(np.linalg.norm(np.cross(A - O, B - O)), 0):
                # Update the angle with the new lines
                mob.become(Angle(line1=line1, line2=line2, radius=0.5, color=YELLOW).move_to(position))

        # Create animation to move the angle along the path
        animation = UpdateFromAlphaFunc(angle, update_angle_position)

        # Play the animation
        self.play(animation, run_time=15, rate_func=linear)

        # Wait for a moment
        self.wait(2)
