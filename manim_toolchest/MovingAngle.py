from manim import *
from tools import INDIGO

class MovingAngle(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Set up angle components
        rotation_center = LEFT
        theta_tracker = ValueTracker(110)
        
        # Create lines
        line1 = Line(LEFT, RIGHT)
        line_moving = Line(LEFT, RIGHT)
        line_ref = line_moving.copy()
        
        # Add circle to hide joining artifact
        origin_dot = Circle(
            radius=0.1, 
            color=WHITE, 
            fill_opacity=1
        ).move_to(rotation_center)
        
        # Rotate the moving line
        line_moving.rotate(
            theta_tracker.get_value() * DEGREES, 
            about_point=rotation_center
        )
        
        # Create angle and label
        angle = Angle(line1, line_moving, radius=0.5, other_angle=False)
        theta_label = MathTex(r"\theta").move_to(
            Angle(
                line1, 
                line_moving, 
                radius=0.5 + 3 * SMALL_BUFF, 
                other_angle=False
            ).point_from_proportion(0.5)
        )

        # Add elements to scene
        self.add(line1, line_moving, angle, theta_label, origin_dot)
        self.wait()

        # Add updaters
        line_moving.add_updater(
            lambda x: x.become(line_ref.copy()).rotate(
                theta_tracker.get_value() * DEGREES, 
                about_point=rotation_center
            )
        )

        angle.add_updater(
            lambda x: x.become(
                Angle(line1, line_moving, radius=0.5, other_angle=False)
            )
        )
        
        theta_label.add_updater(
            lambda x: x.move_to(
                Angle(
                    line1, 
                    line_moving, 
                    radius=0.5 + 3 * SMALL_BUFF, 
                    other_angle=False
                ).point_from_proportion(0.5)
            )
        )

        # Animate angle changes
        self.play(theta_tracker.animate.set_value(40))
        self.play(theta_tracker.animate.increment_value(140))
        self.play(theta_label.animate.set_color(RED), run_time=0.5)
        self.play(theta_tracker.animate.set_value(350))
