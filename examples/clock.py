from manim import *
from tools import INDIGO

class ClockAssembly(VGroup):
    def __init__(self, radius=2, **kwargs):
        super().__init__(**kwargs)
        # Clock Face
        self.circle = Circle(radius=radius, color=WHITE)
        
         # Minute Tick Marks
        self.minute_ticks = VGroup(*[
            Line(
                start=self.circle.point_at_angle(angle),
                end=self.circle.point_at_angle(angle) * 0.9,  # Slightly shorter
                stroke_width=1,
                color=WHITE
            )
            for angle in np.linspace(0, TAU, 60, endpoint=False)
        ])
        
        # Hour Tick Marks
        self.hour_ticks = VGroup(*[
            Line(
                start=self.circle.point_at_angle(angle),
                end=self.circle.point_at_angle(angle) * 0.8,  # Slightly shorter
                stroke_width=3,
                color=WHITE
            )
            for angle in np.linspace(0, TAU, 12, endpoint=False)
        ])
        
        import datetime

        now = datetime.datetime.now()
        # Hands (hour, minute, second)
        self.hour_hand = Line(
            ORIGIN, self.circle.radius * 0.5 * RIGHT, stroke_width=4, color=BLUE
        )
        self.minute_hand = Line(
            ORIGIN, self.circle.radius * 0.7 * RIGHT, stroke_width=3, color=GREEN
        )
        self.second_hand = Line(
            ORIGIN, self.circle.radius * 0.9 * RIGHT, stroke_width=2, color=RED
        )

        # Initialize hand positions
        self.hour_hand.rotate(
            (now.hour % 12 + now.minute / 60) / 12 * TAU, about_point=ORIGIN
        )
        self.minute_hand.rotate(now.minute / 60 * TAU, about_point=ORIGIN)
        self.second_hand.rotate(now.second / 60 * TAU, about_point=ORIGIN)

        # Add all elements
        self.add(self.circle, self.minute_ticks, self.hour_ticks, 
                 self.hour_hand, self.minute_hand, self.second_hand)

    def update_hands(self):
        import datetime
        now = datetime.datetime.now()
        hour_angle = ((now.hour % 12 + now.minute / 60) / 12) * TAU
        minute_angle = (now.minute / 60) * TAU
        second_angle = (now.second / 60) * TAU

        self.hour_hand.become(
            Line(ORIGIN, self.circle.radius * 0.5 * RIGHT, stroke_width=4, color=BLUE).rotate(
                hour_angle, about_point=ORIGIN
            )
        )
        self.minute_hand.become(
            Line(ORIGIN, self.circle.radius * 0.7 * RIGHT, stroke_width=3, color=GREEN).rotate(
                minute_angle, about_point=ORIGIN
            )
        )
        self.second_hand.become(
            Line(ORIGIN, self.circle.radius * 0.9 * RIGHT, stroke_width=2, color=RED).rotate(
                second_angle, about_point=ORIGIN
            )
        )

class Clock(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        # Create clock object
        clock = ClockAssembly(radius=3)
        self.add(clock)

        # Animate clock movement
        self.play(clock.animate.shift(LEFT * 2))

        # Add updater to clock to update hands every frame
        clock.add_updater(lambda mob, dt: mob.update_hands())

        self.wait(10)

        # Final position
        self.play(clock.animate.shift(RIGHT * 4))
