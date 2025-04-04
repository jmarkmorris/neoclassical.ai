from manim import *

class Clock(VGroup):
    def __init__(self, radius=2, **kwargs):
        super().__init__(**kwargs)
        # Clock Face
        self.circle = Circle(radius=radius, color=WHITE)
        
        # Minute Tick Marks
        self.minute_ticks = VGroup(*[
            Line(
                start=self.circle.point_at_angle(angle),
                end=self.circle.point_at_angle(angle) * 0.9,  # Slightly shorter
                color=WHITE
            )
            for angle in np.linspace(0, TAU, 60, endpoint=False)
        ])
        
        # Hour Tick Marks
        self.hour_ticks = VGroup(*[
            Line(
                start=self.circle.point_at_angle(angle),
                end=self.circle.point_at_angle(angle) * 0.8,  # Slightly shorter
                stroke_width=2,
                color=WHITE
            )
            for angle in np.linspace(0, TAU, 12, endpoint=False)
        ])
        
        # Hands (hour, minute, second)
        self.hour_hand = Line(
            ORIGIN, self.circle.radius * 0.5 * RIGHT, stroke_width=4, color=BLUE
        ).rotate(PI/2)  # Initial hour hand position
        self.minute_hand = Line(
            ORIGIN, self.circle.radius * 0.7 * RIGHT, stroke_width=3, color=GREEN
        ).rotate(PI/2)  # Initial minute hand position
        self.second_hand = Line(
            ORIGIN, self.circle.radius * 0.9 * RIGHT, stroke_width=2, color=RED
        ).rotate(PI/2)  # Initial second hand position

        # Add all elements
        self.add(self.circle, self.minute_ticks, self.hour_ticks, 
                 self.hour_hand, self.minute_hand, self.second_hand)

    def update_hands(self, hour_angle, minute_angle, second_angle):
        self.hour_hand.set_angle(hour_angle)
        self.minute_hand.set_angle(minute_angle)
        self.second_hand.set_angle(second_angle)
class ClockScene(Scene):
    def construct(self):
        # Create clock object
        clock = Clock(radius=3)
        self.add(clock)

        # Animate clock movement
        self.play(clock.animate.shift(LEFT * 2))
        
        # Update hands dynamically (angles in radians)
        self.play(clock.hour_hand.animate.rotate(PI / 6))  # Rotate hour hand
        self.play(clock.minute_hand.animate.rotate(TAU / 12))  # Rotate minute hand
        self.play(clock.second_hand.animate.rotate(TAU / 60))  # Rotate second hand

        # Final position
        self.play(clock.animate.shift(RIGHT * 4))
