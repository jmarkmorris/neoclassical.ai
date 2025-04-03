from manim import *
from tools import INDIGO

class MovingAngle(Scene):
    def construct(self):
        self.camera.background_color = INDIGO

        # Add title
        title = Text("Moving Angle", font="Helvetica Neue", weight="LIGHT", font_size=36)
        title.to_edge(UP, buff=0.5)
        self.add(title)

        # Define the rotation center
        rotation_center = LEFT

        # Create the first line
        line1 = Line(rotation_center, RIGHT, color=BLUE)

        # Create the second line, initially at 30 degrees
        line2 = Line(rotation_center, RIGHT, color=RED).rotate(
            30 * DEGREES, about_point=rotation_center
        )

        # Create the angle, initially at 30 degrees
        angle = Angle(line1, line2, radius=0.5, color=YELLOW)

        # Create the theta label
        theta_label = MathTex(r"\theta")
        theta_label.move_to(
            Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
        )

        # Add the objects to the scene
        self.add(line1, line2, angle, theta_label)

        # Create the animation to rotate line2 to 330 degrees
        rotate_action = Rotate(
            line2,
            angle=300 * DEGREES,  # Rotate by 300 degrees (330 - 30)
            about_point=rotation_center,
            run_time=5,
        )

        # Create the updater for the angle and theta label
        def update_angle(obj):
            obj.become(Angle(line1, line2, radius=0.5, color=YELLOW))

        def update_theta_label(obj):
            obj.move_to(
                Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
            )

        # Add the updaters to the angle and theta label
        angle.add_updater(update_angle)
        theta_label.add_updater(update_theta_label)

        # Play the rotation animation
        self.play(rotate_action)

        # Remove the updaters
        angle.clear_updaters()
        theta_label.clear_updaters()

        self.wait()
