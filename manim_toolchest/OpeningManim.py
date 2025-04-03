from manim import *
from tools import INDIGO, ELECTRIC_PURPLE

class OpeningManim(Scene):
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
        ).next_to(title, DOWN, buff=0.3)
        
        self.add(title, subtitle)
        
        # Create LaTeX examples
        title = Tex(r"This is some \LaTeX")
        basel = MathTex(r"\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}")
        VGroup(title, basel).arrange(DOWN)
        
        # First animation
        self.play(
            Write(title),
            FadeIn(basel, shift=DOWN),
        )
        self.wait()

        # Transform title
        transform_title = Tex("That was a transform").to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStart(*(FadeOut(obj, shift=DOWN) for obj in basel)),
        )
        self.wait()

        # Create grid
        grid = NumberPlane()
        grid_title = Tex("This is a grid", font_size=72)
        grid_title.move_to(transform_title)

        self.add(grid, grid_title)  # Title on top of grid
        self.play(
            FadeOut(title),
            FadeIn(grid_title, shift=UP),
            Create(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        # Apply non-linear transform to grid
        grid_transform_title = Tex(
            r"That was a non-linear function \\ applied to the grid",
        )
        grid_transform_title.move_to(grid_title, UL)
        
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.animate.apply_function(
                lambda p: p + np.array([np.sin(p[1]), np.sin(p[0]), 0]),
            ),
            run_time=3,
        )
        self.wait()
        self.play(Transform(grid_title, grid_transform_title))
        self.wait()

