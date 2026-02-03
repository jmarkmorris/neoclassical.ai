from manim import *
INDIGO = "#4B0082"

import numpy as np

class PointMovingOnShapes(Scene):
    def construct(self):
        self.camera.background_color = INDIGO
        
        # Add title and subtitle
        title = Text(
            "Points Moving on Various Shapes",
            font="Helvetica Neue",
            weight="LIGHT",
            font_size=36
        ).to_edge(UP, buff=0.5)
        
        subtitle = Text(
            "MoveAlongPath with different shapes, colors, and rate functions",
            font="Helvetica Neue",
            weight="LIGHT",
            color=YELLOW,
            font_size=20
        ).next_to(title, DOWN, buff=0.1)
        
        self.add(title, subtitle)
        
        # Create a grid of 6 different shapes (2 rows, 3 columns)
        grid_positions = [
            # Row 1
            [-4, 0.75, 0],  # Moved up by 0.25
            [0, 0.75, 0],   # Moved up by 0.25
            [4, 0.75, 0],   # Moved up by 0.25
            # Row 2
            [-4, -2.25, 0], # Moved up by 0.25
            [0, -2.25, 0],  # Moved up by 0.25
            [4, -2.25, 0],  # Moved up by 0.25
        ]
        
        # Define different shapes and configurations
        shape_configs = [
            {
                "shape_creator": lambda: Circle(radius=1, color=WHITE),
                "dot_color": PURE_BLUE,
                "dot_size": 0.1,
                "rate_func": linear,
                "run_time": 3,
                "label": "Circle with linear rate",
                "creation_animation": GrowFromCenter
            },
            {
                "shape_creator": lambda: Square(side_length=2, color=GREEN),
                "dot_color": RED,
                "dot_size": 0.15,
                "rate_func": smooth,
                "run_time": 3,
                "label": "Square with smooth rate",
                "creation_animation": Create
            },
            {
                "shape_creator": lambda: Triangle(color=YELLOW).scale(1.5),
                "dot_color": PURPLE,
                "dot_size": 0.12,
                "rate_func": there_and_back,
                "run_time": 3,
                "label": "Triangle with there_and_back",
                "creation_animation": DrawBorderThenFill
            },
            {
                "shape_creator": lambda: Star(n=5, outer_radius=1, color=ORANGE),
                "dot_color": TEAL,
                "dot_size": 0.08,
                "rate_func": rush_from,
                "run_time": 3,
                "label": "Star with rush_from",
                "creation_animation": SpinInFromNothing
            },
            {
                "shape_creator": lambda: self.create_heart(color=RED),
                "dot_color": WHITE,
                "dot_size": 0.1,
                "rate_func": there_and_back_with_pause,
                "run_time": 3,
                "label": "Heart with pause",
                "creation_animation": Create
            },
            {
                "shape_creator": lambda: self.create_spiral(color=ELECTRIC_PURPLE),
                "dot_color": YELLOW,
                "dot_size": 0.1,
                "rate_func": smooth,
                "run_time": 3,
                "label": "Spiral with smooth rate",
                "creation_animation": Create
            }
        ]
        
        # Create all shapes and dots
        shapes = []
        dots = []
        labels = []
        
        for i, (position, config) in enumerate(zip(grid_positions, shape_configs)):
            # Create shape and move to position
            shape = config["shape_creator"]()
            shape.move_to(position)
            shapes.append(shape)
            
            # Create dot
            dot = Dot(
                radius=config["dot_size"],
                color=config["dot_color"]
            )
            
            # Position dot at the start of the shape's path
            if isinstance(shape, Circle):
                dot.move_to(shape.point_at_angle(0))
            else:
                # For other shapes, try to get the first point
                try:
                    dot.move_to(shape.get_start())
                except:
                    # Fallback: position relative to shape
                    dot.next_to(shape, RIGHT)
            
            dots.append(dot)
            
            # Create label
            label = Text(
                config["label"],
                font="Helvetica Neue",
                weight="LIGHT",
                font_size=16
            ).next_to(shape, DOWN, buff=0.3)
            labels.append(label)
        
        # First, create all shapes with their respective animations
        creation_animations = []
        for shape, config in zip(shapes, shape_configs):
            creation_animations.append(config["creation_animation"](shape))
        
        self.play(
            *creation_animations,
            run_time=2
        )
        
        # Add all dots and labels
        self.add(*dots, *labels)
        
        # Then animate all dots moving along their paths
        path_animations = []
        for dot, shape, config in zip(dots, shapes, shape_configs):
            path_animations.append(
                MoveAlongPath(
                    dot, 
                    shape, 
                    rate_func=config["rate_func"],
                    run_time=config["run_time"]
                )
            )
        
        self.play(
            *path_animations
        )
        
        self.wait()
    
    def create_heart(self, color=RED):
        """Create a heart shape using a parametric function"""
        heart = ParametricFunction(
            lambda t: np.array([
                16 * np.sin(t) ** 3,
                13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t),
                0
            ]) / 16,
            t_range=[0, TAU],
            color=color
        )
        return heart
    
    def create_spiral(self, color=BLUE, num_turns=3):
        """Create a spiral using a parametric function"""
        spiral = ParametricFunction(
            lambda t: np.array([
                t * np.cos(TAU * t * num_turns),
                t * np.sin(TAU * t * num_turns),
                0
            ]),
            t_range=[0, 1],
            color=color
        )
        spiral.scale(0.8)  # Scale to fit in the grid
        return spiral
