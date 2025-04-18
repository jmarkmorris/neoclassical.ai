from manim import *
INDIGO = "#4B0082"

class LatexPlus(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Manim Introduction Example",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "Write(title) + FadeIn(basel) + Transform(title, transform_title)",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create LaTeX examples with gray background
        title = Tex(r"This is some \LaTeX")
        basel = MathTex(r"\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}")
        
        # Group and center the text
        text_group = VGroup(title, basel).arrange(DOWN)
        text_group.move_to(ORIGIN)  # Center in the screen
        
        # Create gray background
        background = Rectangle(
            width=text_group.width + 0.5,
            height=text_group.height + 0.5,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_width=0
        )
        background.move_to(text_group)
        
        # First animation
        self.play(
            FadeIn(background),
            Write(title),
            FadeIn(basel, shift=DOWN),
        )
        self.wait()

        # Transform title but keep it centered with background
        transform_title = Tex("That was a transform")
        new_group = VGroup(transform_title).move_to(ORIGIN)
        
        # Create new background for transformed title
        new_background = Rectangle(
            width=transform_title.width + 0.5,
            height=transform_title.height + 0.5,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_width=0
        )
        new_background.move_to(new_group)
        
        self.play(
            Transform(background, new_background),
            Transform(title, transform_title),
            LaggedStart(*(FadeOut(obj, shift=DOWN) for obj in basel)),
        )
        self.wait()

        # Create grid
        grid = NumberPlane()
        grid_title = Tex("This is a grid", font_size=72)
        
        # Center the grid title with background
        grid_title.move_to(ORIGIN)
        
        # Create background for grid title
        grid_title_background = Rectangle(
            width=grid_title.width + 0.5,
            height=grid_title.height + 0.5,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_width=0
        )
        grid_title_background.move_to(grid_title)
        
        self.play(
            FadeOut(background),
            FadeOut(title),
            Create(grid, run_time=3, lag_ratio=0.1),
        )
        
        self.play(
            FadeIn(grid_title_background),
            FadeIn(grid_title, shift=UP),
        )
        self.wait()

        # Apply non-linear transform to grid
        grid_transform_title = Tex(
            r"That was a non-linear function \\ applied to the grid",
        )
        
        # Center the transformed title
        grid_transform_title.move_to(ORIGIN)
        
        # Create background for transformed grid title
        transform_title_background = Rectangle(
            width=grid_transform_title.width + 0.5,
            height=grid_transform_title.height + 0.5,
            fill_color=GRAY,
            fill_opacity=0.8,
            stroke_width=0
        )
        transform_title_background.move_to(grid_transform_title)
        
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.animate.apply_function(
                lambda p: p + np.array([np.sin(p[1]), np.sin(p[0]), 0]),
            ),
            run_time=3,
        )
        self.wait()
        
        self.play(
            Transform(grid_title_background, transform_title_background),
            Transform(grid_title, grid_transform_title)
        )
        self.wait()

