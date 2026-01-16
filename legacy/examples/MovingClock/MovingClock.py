# Assuming the necessary imports are already done:
from manim import *
import numpy as np # Make sure numpy is imported
import datetime
INDIGO = "#4B0082"


class ClockAssembly(VGroup):
    def __init__(self, radius=2, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius # Store radius for later use
        # Clock Face
        self.circle = Circle(radius=self.radius, color=WHITE)
        self.center_dot = Dot(self.circle.get_center(), radius=0.05, color=WHITE).set_z_index(3) # Ensure dot is on top

        # Minute Tick Marks
        self.minute_ticks = VGroup(*[
            Line(
                start=self.circle.point_at_angle(angle),
                end=self.circle.point_at_angle(angle) * 0.95, # Adjusted length relative to center
                stroke_width=1,
                color=WHITE
            )
            for angle in np.linspace(0, TAU, 60, endpoint=False)
        ])

        # Hour Tick Marks
        self.hour_ticks = VGroup(*[
            Line(
                start=self.circle.point_at_angle(angle),
                end=self.circle.point_at_angle(angle) * 0.85, # Adjusted length relative to center
                stroke_width=3,
                color=WHITE
            )
            for angle in np.linspace(0, TAU, 12, endpoint=False)
        ])

        # Determine initial time *once* during init
        now = datetime.datetime.now()
        initial_hour_angle = -(((now.hour % 12 + now.minute / 60) / 12) * TAU) + PI / 2
        initial_minute_angle = -((now.minute / 60) * TAU) + PI / 2
        initial_second_angle = -((now.second / 60) * TAU) + PI / 2

        # Hands (hour, minute, second) - define length relative to radius
        # Create them pointing upwards (PI/2) initially for easier rotation calculation
        self.hour_hand = Line(
            ORIGIN, UP * self.radius * 0.5, stroke_width=6, color=BLUE
        ).set_z_index(1) # Ensure hands are on top
        self.minute_hand = Line(
            ORIGIN, UP * self.radius * 0.7, stroke_width=4, color=GREEN
        ).set_z_index(1)
        self.second_hand = Line(
            ORIGIN, UP * self.radius * 0.8, stroke_width=2, color=RED
        ).set_z_index(2) # Highest z-index to be on top of other hands

        # Add all static elements first
        self.add(self.circle, self.minute_ticks, self.hour_ticks, self.center_dot)

        # Position hands relative to the circle's center *after* adding static parts
        # This ensures they are positioned correctly even if the VGroup is initialized
        # away from ORIGIN (though usually it starts at ORIGIN).
        center = self.circle.get_center() # Should be ORIGIN if VGroup created at default position
        self.hour_hand.move_to(center, aligned_edge=DOWN)
        self.minute_hand.move_to(center, aligned_edge=DOWN)
        self.second_hand.move_to(center, aligned_edge=DOWN)

        # Apply initial rotation around the clock's center
        self.hour_hand.rotate(initial_hour_angle, about_point=center)
        self.minute_hand.rotate(initial_minute_angle, about_point=center)
        self.second_hand.rotate(initial_second_angle, about_point=center)

        # Add hands *after* positioning them correctly
        self.add(self.hour_hand, self.minute_hand, self.second_hand)


    def update_hands(self, dt): # Pass dt even if not used, standard for updaters
        """Updates hand positions based on current time, relative to the clock's center."""
        now = datetime.datetime.now()
        # Calculate angles: Clockwise, 0 angle is UP (like a real clock)
        # Angle = (fraction of circle) * TAU. Negative sign for clockwise. Add PI/2 because 0 rad is RIGHT.
        
        # Slow down hour hand (e.g., 0.5x speed)
        hour_progress = (now.hour % 12 + now.minute / 60 + now.second / 3600) * 0.5
        target_hour_angle = -((hour_progress / 12) * TAU) + PI/2
        
        # Speed up minute hand (e.g., 10x speed) - use modulo to keep it within 60 'minutes'
        minute_progress = (now.minute + now.second / 60) * 10
        target_minute_angle = -(((minute_progress % 60) / 60) * TAU) + PI/2
        
        # Keep second hand at double speed
        target_second_angle = -(((now.second * 2) % 60) / 60 * TAU) + PI/2

        # Get the current center of the clock
        center = self.circle.get_center()
        
        # Use absolute positioning method - more reliable for clock hands
        # Reset hands to initial position (pointing UP)
        self.hour_hand.become(Line(
            start=center,
            end=center + UP * self.radius * 0.5, 
            stroke_width=6, 
            color=BLUE
        ).set_z_index(1))
        
        self.minute_hand.become(Line(
            start=center,
            end=center + UP * self.radius * 0.7, 
            stroke_width=4, 
            color=GREEN
        ).set_z_index(1))
        
        self.second_hand.become(Line(
            start=center,
            end=center + UP * self.radius * 0.8, 
            stroke_width=2, 
            color=RED
        ).set_z_index(2))
        
        # Rotate to target angles
        self.hour_hand.rotate(target_hour_angle - PI/2, about_point=center)
        self.minute_hand.rotate(target_minute_angle - PI/2, about_point=center)
        self.second_hand.rotate(target_second_angle - PI/2, about_point=center)
        
        # No need to call self.add() again here, we are modifying existing mobjects


class Clock(Scene):
    def construct(self):
        # Assuming INDIGO is defined (e.g., INDIGO = "#4B0082")
        try:
            self.camera.background_color = INDIGO
        except NameError:
            print("Warning: INDIGO color not defined, using default background.")
            pass # Use default background if INDIGO is missing

        # Create clock object and add it directly to the scene
        clock = ClockAssembly(radius=2 * 0.95 * 0.95) # Start at center, reduced size by another 5%
        self.add(clock)  # Add directly without animation

        # Add updater to clock to update hands every frame right from the start
        clock.add_updater(lambda mob, dt: mob.update_hands(dt))
        
        # Create a complex path for the clock to follow
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
        
        # Move the clock along the path continuously
        self.play(
            MoveAlongPath(clock, path),
            run_time=15,           # Longer runtime for smooth movement
            rate_func=linear       # Constant speed along the path
        )
        
        # Let it run in the final position for a moment
        self.wait(2)
        
        # Important: Remove updater at the end of the scene
        clock.remove_updater(clock.update_hands)
