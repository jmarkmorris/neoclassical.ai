from manim import *
from tools import INDIGO

class MovingAngle(Scene):
    def construct(self):
        self.camera.background_color = INDIGO

        # Add title
        title = Text("Moving Angle", font="Helvetica Neue", weight="LIGHT", font_size=36)
        title.to_edge(UP, buff=0.5)
        self.add(title)

        # Set up angle components
        rotation_center = LEFT
        theta_tracker = ValueTracker(0)
        line1 = Line(rotation_center, RIGHT, color=BLUE)
        line2 = Line(rotation_center, RIGHT, color=RED)

        # Rotate line2 based on tracker value
        line2.add_updater(
            lambda x: x.become(Line(rotation_center, RIGHT, color=RED)).rotate(
                theta_tracker.get_value() * DEGREES, about_point=rotation_center
            )
        )

        # Create angle and label
        angle = Angle(line1, line2, radius=0.5, color=YELLOW)
        theta_label = MathTex(r"\theta").move_to(
            Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
        )

        # Add updaters
        angle.add_updater(
            lambda x: x.become(Angle(line1, line2, radius=0.5, color=YELLOW))
        )
        theta_label.add_updater(
            lambda x: x.move_to(
                Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
            )
        )

        # Add elements to scene
        self.add(line1, line2, angle, theta_label)

        # Animate angle change
        # Set up angle components
        rotation_center = ORIGIN
        theta_tracker = ValueTracker(0)
        line1 = Line(rotation_center, RIGHT, color=BLUE)
        line2 = Line(rotation_center, RIGHT, color=RED)
        line2.add_updater(
            lambda x: x.become(Line(rotation_center, RIGHT, color=RED)).rotate(
                theta_tracker.get_value() * DEGREES, about_point=rotation_center
            )
        )

        # Create angle and label
        angle = Angle(line1, line2, radius=0.5, color=YELLOW)
        angle.add_updater(
            lambda x: x.become(Angle(line1, line2, radius=0.5, color=YELLOW))
        )
        theta_label = MathTex(r"\theta").move_to(
            Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
        )
        theta_label.add_updater(
            lambda x: x.move_to(
                Angle(line1, line2, radius=0.5 + 3 * SMALL_BUFF).point_from_proportion(0.5)
            )
        )

        # Add elements to scene
        self.add(line1, line2, angle, theta_label)

        # Animate angle change
        self.play(theta_tracker.animate.set_value(120))
        self.play(theta_tracker.animate.set_value(30))
        self.wait()
