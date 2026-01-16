from manim import *
import numpy as np
# Import the AngleGroup from the npqg library
from npqg import AngleGroup

INDIGO = "#4B0082"

class AnglePath(Scene):
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

        initial_alpha = 0.001  # Start slightly off 0 to avoid initial degenerate angle
        animation_duration = 15.0

        # Create the AngleGroup instance
        angle_group = AngleGroup(
            initial_alpha=initial_alpha,
            path=path,
            duration=animation_duration
        )

        # Add the standard updater
        # The AngleGroup's update method handles movement and angle changes
        angle_group.add_updater(lambda mob, dt: mob.update(dt))

        # Add the AngleGroup to the scene
        self.add(angle_group)

        # Wait for the duration of the animation for the updater to run
        self.wait(animation_duration)

        # Optional: Remove updater after animation completes
        angle_group.clear_updaters()

        # Wait for a moment at the end
        self.wait(2)
