"""
Galaxy scene implementation for NPQG Zoom Animation
Represents a galaxy at the 10^21 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class GalaxyScene(ZoomableScene):
    """Scene representing a galaxy at 10^21 m scale"""
    
    def __init__(self, config, scale_value=21):
        """
        Initialize the galaxy scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 21 (10^21 m)
        """
        super().__init__(config, scale_value, "Galaxy")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Galaxy scene elements")
        elements = []
        
        try:
            # Create the main galaxy object
            galaxy_radius = 3
            galaxy_circle = Circle(
                radius=galaxy_radius,
                stroke_color=WHITE,
                stroke_width=2,
                fill_opacity=0
            )
            galaxy_label = Text(
                "Galaxy",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=WHITE
            )
            galaxy = VGroup(galaxy_circle, galaxy_label)
            elements.append(galaxy)
            
            # Create the galaxy core
            try:
                galaxy_core = self._create_galaxy_core()
                elements.append(galaxy_core)
            except Exception as e:
                print(f"Error creating galaxy core: {e}")
            
            # Create the spiral arms
            try:
                spiral_arms = self._create_spiral_arms()
                elements.append(spiral_arms)
            except Exception as e:
                print(f"Error creating spiral arms: {e}")
            
            # Create stars in the galaxy
            try:
                stars = self._create_stars()
                elements.append(stars)
            except Exception as e:
                print(f"Error creating stars: {e}")
            
            # Create dark matter halo (subtly visible)
            try:
                dark_matter = self._create_dark_matter_halo()
                elements.append(dark_matter)
            except Exception as e:
                print(f"Error creating dark matter halo: {e}")
            
            print(f"Created {len(elements)} Galaxy scene elements")
            return elements
        except Exception as e:
            print(f"Error in Galaxy.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_galaxy_core(self):
        """Create the bright central core of the galaxy"""
        # Create a bright central bulge
        core = VGroup()
        
        # Main central bulge
        central_bulge = Circle(
            radius=0.6,
            fill_color="#FFD700",  # Gold color
            fill_opacity=0.7,
            stroke_width=0
        )
        
        # Brighter center
        inner_core = Circle(
            radius=0.3,
            fill_color="#FFFFFF",
            fill_opacity=0.9,
            stroke_width=0
        )
        
        # Add some texture to the core
        core_texture = VGroup()
        for _ in range(30):
            # Generate points within the bulge using polar coordinates
            r = np.random.uniform(0, 0.55)  # Keep within bulge
            theta = np.random.uniform(0, TAU)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Vary brightness based on distance from center
            brightness = 1 - r / 0.6
            
            # Create a small dot
            dot = Dot(
                point=[x, y, 0],
                radius=np.random.uniform(0.01, 0.03),
                color=WHITE,
                fill_opacity=brightness
            )
            core_texture.add(dot)
        
        core.add(central_bulge, inner_core, core_texture)
        return core
    
    def _create_spiral_arms(self):
        """Create the spiral arms of the galaxy"""
        # Create a group for all spiral arm elements
        spiral_arms = VGroup()
        
        # Parameters for the logarithmic spiral
        a = 0.15  # Controls how tightly wound the spiral is
        num_arms = 2  # Number of spiral arms
        points_per_arm = 150  # Number of points per arm
        max_theta = 3 * TAU  # Maximum angle for spiral
        
        # Create spiral arms
        for arm_idx in range(num_arms):
            arm = VGroup()
            # Rotational offset for this arm
            arm_offset = arm_idx * (TAU / num_arms)
            
            for i in range(points_per_arm):
                # Parametric parameter for this point
                t = i / (points_per_arm - 1)
                
                # Theta increases along the arm
                theta = t * max_theta
                
                # Radius increases according to logarithmic spiral formula
                radius = a * np.exp(0.3 * theta) 
                
                # Limit the radius to stay within the scene circle
                radius = min(radius, 2.8)
                
                # Convert to Cartesian coordinates with the arm offset
                x = radius * np.cos(theta + arm_offset)
                y = radius * np.sin(theta + arm_offset)
                
                # Determine size and opacity based on position
                # Less opaque and smaller as we move outward
                base_size = 0.04 * (1 - 0.6 * t)
                size_variation = 0.02 * np.random.random()
                size = base_size + size_variation
                
                opacity = 0.9 - 0.7 * t + 0.2 * np.random.random()
                
                # Add a star/dust particle to the arm
                color = np.random.choice([WHITE, "#FFD700", "#87CEFA"], p=[0.7, 0.2, 0.1])
                
                dot = Dot(
                    point=[x, y, 0],
                    radius=size,
                    color=color,
                    fill_opacity=opacity
                )
                arm.add(dot)
            
            spiral_arms.add(arm)
        
        return spiral_arms
    
    def _create_stars(self):
        """Create stars distributed throughout the galaxy"""
        # Create a group for all stars
        stars = VGroup()
        
        # Number of stars to create
        num_stars = 200
        
        # Maximum radius to keep stars inside the galaxy circle
        max_radius = 2.8
        
        for _ in range(num_stars):
            # Use polar coordinates for distribution
            # Use a distribution that favors the disk but also has some stars in the halo
            r = np.random.power(0.5) * max_radius  # Power distribution gives more stars near center
            theta = np.random.uniform(0, TAU)
            
            # Convert to Cartesian coordinates
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Determine size and color randomly
            size = np.random.uniform(0.005, 0.025)
            
            # Star colors: blue, white, yellow, orange, red in realistic proportions
            color_choices = ["#A2CFFE", "#FFFFFF", "#FFF9B5", "#FFB975", "#FF9E8F"]
            probabilities = [0.1, 0.3, 0.4, 0.15, 0.05]  # Realistic stellar population
            color = np.random.choice(color_choices, p=probabilities)
            
            star = Dot(
                point=[x, y, 0],
                radius=size,
                color=color,
                fill_opacity=np.random.uniform(0.5, 1.0)
            )
            stars.add(star)
        
        return stars
    
    def _create_dark_matter_halo(self):
        """Create a subtle visualization of the dark matter halo"""
        # Create a faint, extended halo
        halo = Circle(
            radius=2.9,  # Slightly smaller than main circle
            fill_color="#2F2F4F",  # Very dark blue
            fill_opacity=0.1,
            stroke_width=0
        )
        
        # Create some subtle texture in the halo
        texture = VGroup()
        for _ in range(50):
            # Use polar coordinates to distribute points in a shell-like pattern
            r = np.random.uniform(2.0, 2.85)  # Mostly in outer regions
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            dot = Dot(
                point=[x, y, 0],
                radius=0.015,
                color="#4B0082",  # Indigo
                fill_opacity=0.1
            )
            texture.add(dot)
        
        return VGroup(halo, texture)