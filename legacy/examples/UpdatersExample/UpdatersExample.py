from manim import *
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"

class UpdatersExample(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Advanced Updaters Example",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Multiple objects with different updaters interacting with each other",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create a central square that will move up and down
        square = Square(side_length=0.8, color=BLUE).shift(UP * 1)  # Smaller square, moved down
        square.set_fill(BLUE, opacity=0.5)
        
        # Create a decimal number that tracks the square's y-position
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
            font_size=36
        )
        
        # Add updaters to the decimal
        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(max(square.get_center()[1], -2.5))) # clamp the position
        
        # Create orbiting dots around the square
        dots = VGroup(*[Dot(color=PURE_RED) for _ in range(8)])
        
        # Position dots in a circle around the square
        for i, dot in enumerate(dots):
            angle = i * PI / 4
            dot.move_to(square.get_center() + np.array([np.cos(angle), np.sin(angle), 0]))
            
            # Add an updater to each dot to orbit around the square
            dot.initial_angle = angle
            dot.add_updater(
                lambda d, dt, i=i: d.move_to(
                    square.get_center() + 
                    np.array([
                        np.cos(d.initial_angle + self.time * (i % 3 + 1)), 
                        np.sin(d.initial_angle + self.time * (i % 3 + 1)), 
                        0
                    ])
                )
            )
        
        # Create a circle that changes size based on square's y-position
        circle = Circle(radius=0.5, color=ELECTRIC_PURPLE)
        circle.set_fill(ELECTRIC_PURPLE, opacity=0.3)
        circle.move_to(LEFT * 4 + UP * 0.5)  # Moved left and up more
        
        # Add updater to the circle to change its size based on square's position
        circle.add_updater(
            lambda c: c.set_width(
                0.5 + abs(max(square.get_center()[1], -2.5)) # clamp the position
            )
        )
        
        # Create a color-changing triangle
        triangle = Triangle(color=YELLOW).scale(0.5)
        triangle.set_fill(YELLOW, opacity=0.5)
        triangle.move_to(RIGHT * 4 + UP * 0.5)  # Moved right and up more
        
        # Add updater to change triangle's color based on square's position
        triangle.add_updater(
            lambda t: t.set_color(
                interpolate_color(
                    YELLOW,
                    PURE_RED,
                    (max(square.get_center()[1], -2.5) + 3) / 6
                )
            )
        )
        
        # Add updater to rotate the triangle
        triangle.add_updater(lambda t, dt: t.rotate(dt))
        
        # Create a trail effect for the square
        trail = VMobject(stroke_width=2, stroke_opacity=0.8)
        trail.set_points_as_corners([square.get_center(), square.get_center()])
        
        def update_trail(trail):
            previous_trail = trail.copy()
            previous_trail.add_points_as_corners([np.array([square.get_center()[0], max(square.get_center()[1], -2.5), 0])]) # clamp the position
            
            # Limit the length of the trail
            if len(previous_trail.get_points()) > 100:
                # Remove the oldest point
                points = previous_trail.get_points()[1:] # Changed from [3:] to [1:]
                previous_trail.set_points(points)
                
            trail.become(previous_trail)
            
            # Fade the trail from start to end
            n_points = len(trail.get_points())
            if n_points > 0:
                colors = [
                    interpolate_color(BLACK, BLUE_A, i/(n_points-1))
                    for i in range(n_points)
                ]
                trail.set_rgba_array_direct(
                    np.array([color_to_rgba(c) for c in colors])
                )
        
        trail.add_updater(update_trail)
        
        # Add all objects to the scene
        self.add(square, decimal, dots, circle, triangle, trail)
        
        # Animate the square moving up and down
        self.play(
            square.animate.to_edge(DOWN),
            rate_func=there_and_back_with_pause,
            run_time=8,
        )
        
        # Now move the square in a smaller circular path
        self.play(
            MoveAlongPath(
                square, 
                Circle(radius=1.5).shift(DOWN * 0.5),  # Smaller circle, moved up
            ),
            run_time=8,
            rate_func=linear
        )
        
        self.wait()
