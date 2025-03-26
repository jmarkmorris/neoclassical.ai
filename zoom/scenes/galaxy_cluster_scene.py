"""
Galaxy Cluster scene implementation for NPQG Zoom Animation
Represents galaxy clusters at the 10^23 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class GalaxyClusterScene(ZoomableScene):
    """Scene representing galaxy clusters at 10^23 m scale"""
    
    def __init__(self, config, scale_value=23):
        """
        Initialize the galaxy cluster scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 23 (10^23 m)
        """
        super().__init__(config, scale_value, "Galaxy Cluster")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Galaxy Cluster scene elements")
        elements = []
        
        try:
            # Create the main cluster object using the base class method
            # This will automatically load custom images if available
            cluster_radius = 3
            cluster = self.create_object(
                "Galaxy Cluster",
                [0, 0, 0], 
                cluster_radius
            )
            elements.append(cluster)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            # Check if we're using custom images and if an image was successfully loaded
            # The image is always the second element in the group if it exists
            has_custom_image = self.use_custom_images and len(cluster) > 2
                    
            if not self.use_custom_images or not has_custom_image:
                # Add intergalactic medium (dark matter and gas)
                try:
                    medium = self._create_intergalactic_medium()
                    elements.append(medium)
                except Exception as e:
                    print(f"Error creating intergalactic medium: {e}")
                
                # Add galaxies within the cluster
                try:
                    galaxies = self._create_galaxies()
                    elements.append(galaxies)
                except Exception as e:
                    print(f"Error creating galaxies: {e}")
            
            print(f"Created {len(elements)} Galaxy Cluster scene elements")
            return elements
        except Exception as e:
            print(f"Error in GalaxyCluster.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_galaxies(self):
        """Create a distribution of galaxies within the cluster"""
        # Create galaxy distribution using ellipses of different sizes
        galaxies = VGroup()
        
        # Maximum radius to keep all galaxies inside the cluster circle
        max_radius = 2.5  # Slightly smaller than the main cluster circle
        
        # Add 15-20 galaxies of different types and sizes
        for i in range(18):
            # Use a bounded normal distribution for radial position
            # This creates a cluster effect (more galaxies in center)
            r_unbounded = np.random.normal(0, max_radius/2)  # Normal distribution
            r = min(abs(r_unbounded), max_radius * 0.9)  # Bound it to stay inside
            theta = np.random.uniform(0, TAU)  # Random angle
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Galaxy types (spiral, elliptical, irregular)
            galaxy_type = np.random.choice(["spiral", "elliptical", "irregular"], p=[0.6, 0.3, 0.1])
            
            # Adjust sizes to be smaller than in original code
            # This ensures they don't extend beyond their locations
            if galaxy_type == "spiral":
                # Spiral galaxy
                size = np.random.uniform(0.08, 0.2)
                galaxy = self._create_spiral_galaxy(size)
            elif galaxy_type == "elliptical":
                # Elliptical galaxy
                size = np.random.uniform(0.1, 0.3)
                galaxy = self._create_elliptical_galaxy(size)
            else:
                # Irregular galaxy
                size = np.random.uniform(0.08, 0.2)
                galaxy = self._create_irregular_galaxy(size)
            
            galaxy.move_to([x, y, 0])
            
            # Random rotation
            galaxy.rotate(np.random.uniform(0, TAU))
            
            galaxies.add(galaxy)
        
        return galaxies
    
    def _create_spiral_galaxy(self, size):
        """Create a simplified spiral galaxy visualization"""
        center = Dot(radius=size/5, color=WHITE, fill_opacity=0.9)
        
        # Create spiral arms
        arms = VGroup()
        for i in range(2):  # Two spiral arms
            arm = VGroup()
            for j in range(20):
                t = j / 19  # Parameter from 0 to 1
                radius = size * (0.2 + t * 0.8)  # Spiral radius increasing with t
                angle = 3 * TAU * t + i * PI  # Angular position including arm offset
                
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                
                dot = Dot(
                    point=[x, y, 0],
                    radius=size/15,
                    color=WHITE,
                    fill_opacity=0.7 - 0.5 * t  # Fade out along the arm
                )
                arm.add(dot)
            arms.add(arm)
        
        return VGroup(center, arms)
    
    def _create_elliptical_galaxy(self, size):
        """Create a simplified elliptical galaxy visualization"""
        # Elliptical galaxies have a smooth light distribution
        ellipse = Ellipse(
            width=size * 1.5,
            height=size,
            fill_color=WHITE,
            fill_opacity=0.7,
            stroke_width=0
        )
        
        # Add some random stars for texture
        stars = VGroup(*[
            Dot(
                point=[
                    np.random.normal(0, size/2.5), 
                    np.random.normal(0, size/3.5), 
                    0
                ],
                radius=0.01,
                color=WHITE,
                fill_opacity=np.random.uniform(0.3, 0.9)
            )
            for _ in range(15)
        ])
        
        return VGroup(ellipse, stars)
    
    def _create_irregular_galaxy(self, size):
        """Create a simplified irregular galaxy visualization"""
        # Irregular galaxies have no defined shape
        # Create a random collection of star clusters
        clusters = VGroup(*[
            Dot(
                point=[
                    np.random.uniform(-size, size),
                    np.random.uniform(-size, size),
                    0
                ],
                radius=np.random.uniform(size/20, size/10),
                color=WHITE,
                fill_opacity=np.random.uniform(0.4, 0.9)
            )
            for _ in range(10)
        ])
        
        return clusters
    
    def _create_intergalactic_medium(self):
        """Create a visualization of the intergalactic medium"""
        # Create a faint cloud representing hot gas and dark matter
        circle_radius = 2.8  # Match radius to the main circle
        medium = Circle(
            radius=circle_radius,
            fill_color="#8A2BE2",  # Blueish-purple
            fill_opacity=0.1,
            stroke_width=0
        )
        
        # Add texture with random dots - ensuring they stay within the circle
        texture_dots = []
        for _ in range(100):
            # Use polar coordinates to ensure dots stay inside the circle
            r = np.random.uniform(0, circle_radius * 0.95)  # Stay within 95% of radius
            theta = np.random.uniform(0, 2 * np.pi)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            dot = Dot(
                point=[x, y, 0],
                radius=0.02,
                color="#4B0082",  # Indigo
                fill_opacity=0.1
            )
            texture_dots.append(dot)
        
        texture = VGroup(*texture_dots)
        
        return VGroup(medium, texture)