from manim import *
import numpy as np
import random

class AnimatedAngle(Scene):
    def construct(self):
        # Define the rotation center
        rotation_center = np.array([0, 0, 0])

        # Define the initial and final angles in degrees
        initial_angle_deg = random.uniform(10, 170)  # Ensure non-zero initial angle
        final_angle_deg = random.uniform(190, 350)    # Ensure non-zero final angle

        # Create the first line
        line1 = Line(rotation_center, RIGHT)
        # Create the second line, initially rotated to the initial angle
        line2 = Line(rotation_center, RIGHT).rotate(initial_angle_deg * DEGREES, about_point=rotation_center)

        # Create the angle
        angle = Angle(line1, line2, radius=0.5)

        # Create the animation for line2 to rotate to the final angle
        rotate_animation = Rotate(
            line2,
            angle=(final_angle_deg - initial_angle_deg) * DEGREES,
            about_point=rotation_center,
            run_time=3
        )

        # Add the lines and angle to the scene
        self.add(line1, line2, angle)

        # Play the rotation animation
        self.play(rotate_animation)

        self.wait()
