"""
Manim Toolchest Utilities

This module contains utility functions and code snippets that can be reused
across different Manim animations in the toolchest.
"""

from manim import *
import json

# Common colors
INDIGO = "#4B0082"
ELECTRIC_PURPLE = "#8F00FF"

def add_grid(scene, color=INDIGO):
    """
    Add a grid to the scene for easier positioning and layout.
    
    Args:
        scene: The Manim scene to add the grid to
        color: The color of the grid lines (default: INDIGO)
    
    Returns:
        The grid object that was added to the scene
    """
    grid = NumberPlane(
        x_range=[-7, 7],
        y_range=[-4, 4],
        axis_config={
            "stroke_color": WHITE,
            "stroke_width": 1,
            "include_ticks": False,
            "include_tip": False,
        },
        background_line_style={
            "stroke_color": color,
            "stroke_width": 1,
        }
    )
    scene.add(grid)
    return grid

def create_kwargs_example():
    """
    Example of using kwargs for cleaner parameter passing.
    """
    kwargs = {
        'side_length': 5, 
        'stroke_color': GREEN, 
        'fill_color': BLUE, 
        'fill_opacity': 0.75
    }
    return kwargs

def print_dict(dictionary):
    """
    Print a dictionary in a readable format.
    
    Args:
        dictionary: The dictionary to print
    """
    json_string = json.dumps(dictionary, indent=4)
    print(json_string)
    return json_string

class KwargsExample(Scene):
    """Example scene showing how to use kwargs for cleaner code"""
    def construct(self):
        kwargs = create_kwargs_example()
        sq = Square(**kwargs)
        self.play(Create(sq), run_time=3, subcaption="Using kwargs for cleaner code", subcaption_duration=3)
        self.wait()
