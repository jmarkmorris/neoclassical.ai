"""
Universe scale scene implementation for NPQG Zoom Animation
Represents the observable universe at the 10^26 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class UniverseScene(ZoomableScene):
    """Scene representing the observable universe at 10^26 m scale"""
    
    def __init__(self, config, scale_value=26):
        """
        Initialize the universe scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 26 (10^26 m)
        """
        super().__init__(config, scale_value, "Universe")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Universe scene elements")
        elements = []
        
        try:
            # Create the observable universe object
            universe_radius = 3
            universe_circle = Circle(
                radius=universe_radius,
                stroke_color=WHITE,
                stroke_width=2,
                fill_opacity=0
            )
            universe_label = Text(
                "Observable Universe",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=WHITE
            )
            universe = VGroup(universe_circle, universe_label)
            elements.append(universe)
            
            # Add cosmic background radiation visualization (subtle blue-red gradient)
            try:
                gradient = self._create_cmb_background()
                elements.append(gradient)
            except Exception as e:
                print(f"Error creating CMB background: {e}")
            
            # Create galaxy cluster distribution (small dots)
            try:
                clusters = self._create_galaxy_clusters()
                elements.append(clusters)
            except Exception as e:
                print(f"Error creating galaxy clusters: {e}")
            
            print(f"Created {len(elements)} Universe scene elements")
            return elements
        except Exception as e:
            print(f"Error in Universe.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_cmb_background(self):
        """Create a visualization of the cosmic microwave background"""
        # Create a subtle gradient representing the CMB
        circle_radius = 2.8  # Match radius to the main circle
        gradient = Circle(
            radius=circle_radius,
            fill_color=None,
            fill_opacity=0.2,
            stroke_width=0
        )
        
        # Create noise texture but ensure all dots are inside the circle
        noise_dots = []
        for _ in range(200):  # 200 small dots
            # Use polar coordinates to ensure dots stay inside circle
            r = np.random.uniform(0, circle_radius * 0.9)  # Stay 10% away from edge
            theta = np.random.uniform(0, 2 * np.pi)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            dot = Dot(
                point=[x, y, 0],
                radius=0.01,
                color=random.choice(["#FF4500", "#4169E1"]),  # Red-blue representing temperature variations
                fill_opacity=0.1
            )
            noise_dots.append(dot)
            
        noise = VGroup(*noise_dots)
        
        return VGroup(gradient, noise)
    
    def _create_galaxy_clusters(self):
        """Create a distribution of galaxy clusters"""
        # Create a group of small dots representing galaxy clusters
        circle_radius = 2.5  # Slightly smaller than the main circle
        
        # Create galaxy clusters using polar coordinates to keep them inside the circle
        cluster_dots = []
        for _ in range(50):  # 50 clusters
            # Use polar coordinates with biased distribution (more clusters near center)
            r = np.random.power(0.5) * circle_radius * 0.95  # Power distribution gives more near center
            theta = np.random.uniform(0, 2 * np.pi)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Vary the size slightly
            size = np.random.uniform(0.02, 0.04)
            
            dot = Dot(
                point=[x, y, 0],
                radius=size,
                color="#FFFFFF",
                fill_opacity=0.5
            )
            cluster_dots.append(dot)
        
        clusters = VGroup(*cluster_dots)
        return clusters