from manim import *
INDIGO = "#4B0082"

class MakeGraph(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Function Graphing Example",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "axes.plot(lambda x: np.sin(x)) + axes.get_graph_label(graph, label)",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create axes
        axes = Axes(
            x_range=[-10, 10.3, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=10,
            y_length=5,  # Make y-axis shorter
            axis_config={"color": GREEN},
            x_axis_config={
                "numbers_to_include": np.arange(-10, 10.01, 2),
                "numbers_with_elongated_ticks": np.arange(-10, 10.01, 2),
            },
            tips=False,
        )
        
        # Add axis labels
        axes_labels = axes.get_axis_labels()
        
        # Plot functions
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)

        # Add graph labels
        sin_label = axes.get_graph_label(
            sin_graph, "\\sin(x)", x_val=-10, direction=UP / 2
        )
        cos_label = axes.get_graph_label(cos_graph, label="\\cos(x)")

        # Add vertical line at x=2π
        vert_line = axes.get_vertical_line(
            axes.i2gp(TAU, cos_graph), color=YELLOW, line_func=Line
        )
        line_label = axes.get_graph_label(
            cos_graph, "x=2\\pi", x_val=TAU, direction=UR, color=WHITE
        )

        # Group elements and add to scene
        plot = VGroup(axes, sin_graph, cos_graph, vert_line)
        labels = VGroup(axes_labels, sin_label, cos_label, line_label)
        
        # Move the plot down to avoid subtitle overlap
        plot.shift(DOWN * 0.7)  # Increased from 0.5 to 0.7
        labels.shift(DOWN * 0.7)
        
        self.add(plot, labels)
