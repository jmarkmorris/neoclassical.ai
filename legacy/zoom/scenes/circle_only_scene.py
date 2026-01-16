"""
Circle-only scene implementation for NPQG Universe Zoom Animation
Only creates circle objects without text labels
"""

import os
import sys
from manim import *

# Add the project root to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.image_loader import ImageLoader
from scenes.base_scene import ZoomableScene

class CircleOnlyScene(ZoomableScene):
    """Scene that only creates circles without labels"""
    
    def get_elements(self):
        """
        Return only circle elements without embedded labels
        
        Returns:
            list: A list of elements to add to the scene
        """
        # Extract settings from config
        fill_color = self.config["global_settings"].get("fill_color", "#3366CC")
        fill_opacity = self.config["global_settings"].get("fill_opacity", 0.8)
        circle_color = self.config["global_settings"].get("color_circle", "#FFFFFF")
        stroke_width = self.config["global_settings"].get("stroke_width", 2)
        
        # Create a circle at the origin
        circle = Circle(
            radius=3,
            stroke_color=circle_color,
            stroke_width=stroke_width,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            z_index=1  # Ensure circle is above background
        )
        
        # Return a list containing just the circle
        return [circle]
