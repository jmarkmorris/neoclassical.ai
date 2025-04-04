from manim import *
import numpy as np

INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"
WHITE = "#FFFFFF"
YELLOW = "#FFFF00"
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

        # Create new lines
        line1 = Line(O, A, color=WHITE)
        line2 = Line(O, B, color=WHITE)

        # Create the angle object
        angle = Angle(line1, line2, radius=0.5, color=WHITE)
        self.angle_group = VGroup(line1, line2, angle)
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
            
            # Create new lines
            line1 = Line(O, A, color=WHITE).move_to(position)
            line2 = Line(O, B, color=WHITE).move_to(position)

            # Check if lines are parallel
            if not np.isclose(np.linalg.norm(np.cross(A - O, B - O)), 0):
                # Update the angle with the new lines
                new_angle = Angle(line1, line2, color=YELLOW, radius=0.5).move_to(position)
                mob.become(VGroup(line1, line2, new_angle))
            else:
                # If lines are parallel, keep the previous state
                pass
            mob.move_to(position)

        # Create animation to move the angle along the path
        animation = UpdateFromAlphaFunc(self.angle_group, update_angle_position)

        # Play the animation
        self.play(animation, run_time=15, rate_func=linear)

        # Wait for a moment
        self.wait(2)
