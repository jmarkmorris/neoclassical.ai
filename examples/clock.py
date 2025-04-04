# Assuming the necessary imports are already done:
from manim import *
import numpy as np # Make sure numpy is imported
import datetime
from tools import INDIGO # Assuming tools.py exists with INDIGO defined

# --- Helper function (optional but clean) ---
# This is available directly in newer Manim versions, but defining it ensures compatibility
# or provides clarity if you're using an older version. Manim's rotate_vector works too.
def rotate_vector(vec, angle):
    """Rotates a 2D vector by a given angle."""
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    return np.array([
        vec[0] * cos_a - vec[1] * sin_a,
        vec[0] * sin_a + vec[1] * cos_a,
        vec[2] # Keep z-component if it exists
    ])

class ClockAssembly(VGroup):
    def __init__(self, radius=2, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius # Store radius for later use
        # Clock Face
        self.circle = Circle(radius=self.radius, color=WHITE)
        self.center_dot = Dot(self.circle.get_center(), radius=0.05, color=WHITE) # Optional center dot

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

        # Hands (hour, minute) - define length relative to radius
        # Create them pointing upwards (PI/2) initially for easier rotation calculation
        self.hour_hand = Line(
            ORIGIN, UP * self.radius * 0.5, stroke_width=6, color=BLUE
        ).set_z_index(1) # Ensure hands are on top
        self.minute_hand = Line(
            ORIGIN, UP * self.radius * 0.7, stroke_width=4, color=GREEN
        ).set_z_index(1)

        # Add all static elements first
        self.add(self.circle, self.minute_ticks, self.hour_ticks, self.center_dot)

        # Position hands relative to the circle's center *after* adding static parts
        # This ensures they are positioned correctly even if the VGroup is initialized
        # away from ORIGIN (though usually it starts at ORIGIN).
        center = self.circle.get_center() # Should be ORIGIN if VGroup created at default position
        self.hour_hand.move_to(center, aligned_edge=DOWN)
        self.minute_hand.move_to(center, aligned_edge=DOWN)

        # Apply initial rotation around the clock's center
        self.hour_hand.rotate(initial_hour_angle, about_point=center)
        self.minute_hand.rotate(initial_minute_angle, about_point=center)

        # Add hands *after* positioning them correctly
        self.add(self.hour_hand, self.minute_hand)

        # Store initial angles if needed for relative updates, though absolute calculation is fine here
        # self.current_hour_angle = initial_hour_angle
        # self.current_minute_angle = initial_minute_angle


    def update_hands(self, dt): # Pass dt even if not used, standard for updaters
        """Updates hand positions based on current time, relative to the clock's center."""
        now = datetime.datetime.now()
        # Calculate angles: Clockwise, 0 angle is UP (like a real clock)
        # Angle = (fraction of circle) * TAU. Negative sign for clockwise. Add PI/2 because 0 rad is RIGHT.
        target_hour_angle = -(((now.hour % 12 + now.minute / 60 + now.second / 3600) / 12) * TAU) + PI/2
        target_minute_angle = -(((now.minute + now.second / 60) / 60) * TAU) + PI/2
        # target_second_angle = -((now.second / 60) * TAU) + PI/2 # Example if you add a second hand

        # --- Method 1: Set angle directly (Simpler if hands start aligned) ---
        # Get the current center of the VGroup (which includes the circle and hands)
        center = self.get_center() # THIS IS THE KEY CHANGE

        # Reset the hands to a known orientation (e.g., pointing UP) relative to the center
        # then rotate to the target angle around the center.
        self.hour_hand.set_angle(PI/2, about_point=center) # Reset to UP
        self.hour_hand.rotate(target_hour_angle - PI/2, about_point=center) # Rotate to target

        self.minute_hand.set_angle(PI/2, about_point=center) # Reset to UP
        self.minute_hand.rotate(target_minute_angle - PI/2, about_point=center) # Rotate to target


        # --- Method 2: Calculate endpoints (More robust, less reliant on initial state) ---
        # center = self.get_center() # Get current center
        # hour_vector = UP * self.radius * 0.5
        # minute_vector = UP * self.radius * 0.7
        #
        # rotated_hour_vector = rotate_vector(hour_vector, target_hour_angle - PI/2) # Adjust angle based on initial vector orientation
        # rotated_minute_vector = rotate_vector(minute_vector, target_minute_angle- PI/2)
        #
        # self.hour_hand.put_start_and_end_on(center, center + rotated_hour_vector)
        # self.minute_hand.put_start_and_end_on(center, center + rotated_minute_vector)

        # No need to call self.add() again here, we are modifying existing mobjects


class ClockScene(Scene):
    def construct(self):
        # Assuming INDIGO is defined (e.g., INDIGO = "#4B0082")
        try:
            self.camera.background_color = INDIGO
        except NameError:
            print("Warning: INDIGO color not defined, using default background.")
            pass # Use default background if INDIGO is missing

        # Create clock object
        clock = ClockAssembly(radius=2).shift(UP * 1) # Example: Create slightly offset
        self.play(Create(clock))
        self.wait(0.5)

        # Animate clock movement
        self.play(clock.animate.shift(LEFT * 4 + DOWN * 2))
        self.wait(0.5)

        # Add updater to clock to update hands every frame
        # Pass the dt parameter from the lambda function to the method
        clock.add_updater(lambda mob, dt: mob.update_hands(dt))

        # Let the clock run for a while
        self.wait(5)

        # Move the clock again while the updater is active
        self.play(clock.animate.shift(RIGHT * 6))

        # Let it run in the final position
        self.wait(5)

        # Important: Remove updater if the scene ends or the object is removed
        # to prevent potential issues in more complex scenes.
        clock.remove_updater(clock.update_hands)
        self.wait(0.5)
        self.play(FadeOut(clock))
