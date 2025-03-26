"""
Star scene implementation for NPQG Zoom Animation
Represents a star at the 10^9 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class StarScene(ZoomableScene):
    """Scene representing a star at 10^9 m scale"""
    
    def __init__(self, config, scale_value=9):
        """
        Initialize the star scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 9 (10^9 m)
        """
        super().__init__(config, scale_value, "Star")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Star scene elements")
        elements = []
        
        try:
            # Create the main star boundary using the base class method
            # This will automatically load custom images if available
            star_radius = 3
            star_boundary = self.create_object(
                "Star",
                [0, 0, 0],
                star_radius
            )
            elements.append(star_boundary)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            # Check if we're using custom images and if an image was successfully loaded
            # The image is always the second element in the group if it exists
            has_custom_image = self.use_custom_images and len(star_boundary) > 2
                    
            if not self.use_custom_images or not has_custom_image:
                # Create the star
                try:
                    star_body = self._create_star_body()
                    elements.append(star_body)
                except Exception as e:
                    print(f"Error creating star body: {e}")
                
                # Create the corona
                try:
                    corona = self._create_corona()
                    elements.append(corona)
                except Exception as e:
                    print(f"Error creating corona: {e}")
                
                # Create sunspots
                try:
                    sunspots = self._create_sunspots()
                    elements.append(sunspots)
                except Exception as e:
                    print(f"Error creating sunspots: {e}")
                
                # Create flares and prominences
                try:
                    flares = self._create_flares()
                    elements.append(flares)
                except Exception as e:
                    print(f"Error creating flares: {e}")
            
            print(f"Created {len(elements)} Star scene elements")
            return elements
        except Exception as e:
            print(f"Error in Star.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_star_body(self):
        """Create the main body of the star"""
        star_body = VGroup()
        
        # Create the main layers of the star from inside out
        
        # Core (extremely hot, white-blue)
        core = Circle(
            radius=0.7,
            fill_color="#FFFFFF",
            fill_opacity=1.0,
            stroke_width=0
        )
        
        # Radiative zone (yellow-white)
        radiative_zone = Circle(
            radius=1.5,
            fill_color="#FFFACD",  # Lemon chiffon
            fill_opacity=0.9,
            stroke_width=0
        )
        
        # Convective zone (orange-yellow)
        convective_zone = Circle(
            radius=2.1,
            fill_color="#FFD700",  # Gold
            fill_opacity=0.8,
            stroke_width=0
        )
        
        # Photosphere (visible surface - yellow-orange)
        photosphere = Circle(
            radius=2.4,
            fill_color="#FFA500",  # Orange
            fill_opacity=0.7,
            stroke_width=0
        )
        
        # Add layers from bottom to top
        star_body.add(radiative_zone, core)
        star_body.add(convective_zone, photosphere)
        
        # Add granulation texture to the surface
        granulation = self._create_granulation()
        star_body.add(granulation)
        
        return star_body
    
    def _create_granulation(self):
        """Create the granulation pattern on the star's surface"""
        granulation = VGroup()
        
        # Surface radius
        surface_radius = 2.4
        
        # Number of granules
        num_granules = 200
        
        for _ in range(num_granules):
            # Use polar coordinates to keep granules on the surface
            # We'll create granules slightly below the surface
            r = np.random.uniform(surface_radius * 0.85, surface_radius * 0.98)
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Size varies but stays small
            size = np.random.uniform(0.05, 0.15)
            
            # Create a soft-edged circle for each granule
            granule = Circle(
                radius=size,
                fill_color="#FFFF00",  # Bright yellow
                fill_opacity=np.random.uniform(0.3, 0.6),
                stroke_width=0
            )
            granule.move_to([x, y, 0])
            
            granulation.add(granule)
        
        return granulation
    
    def _create_corona(self):
        """Create the star's corona (outer atmosphere)"""
        corona = VGroup()
        
        # Base corona glow
        base_corona = Circle(
            radius=2.8,
            fill_color="#FFD700",  # Gold
            fill_opacity=0.2,
            stroke_width=0
        )
        
        # Outer corona glow
        outer_corona = Circle(
            radius=2.9,
            fill_color="#FFA500",  # Orange
            fill_opacity=0.1,
            stroke_width=0
        )
        
        corona.add(base_corona, outer_corona)
        
        # Add corona streamers
        num_streamers = 24
        for i in range(num_streamers):
            angle = i * TAU / num_streamers
            
            # Vary the length and width
            length = np.random.uniform(0.2, 0.4)
            width = np.random.uniform(0.02, 0.08)
            
            # Start position at the surface
            start_radius = 2.4
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            # End position outside the surface
            end_radius = start_radius + length
            end_x = end_radius * np.cos(angle)
            end_y = end_radius * np.sin(angle)
            
            # Create a streamer using a quadratic Bezier curve
            # Add some curvature
            control_radius = start_radius + length * 0.7
            control_angle = angle + np.random.uniform(-0.2, 0.2)
            control_x = control_radius * np.cos(control_angle)
            control_y = control_radius * np.sin(control_angle)
            
            streamer = CubicBezier(
                start=[start_x, start_y, 0],
                h1=[control_x, control_y, 0],
                h2=[control_x, control_y, 0],
                end=[end_x, end_y, 0],
                stroke_color="#FFFF00",
                stroke_width=width * 100,  # Scale up to be visible
                stroke_opacity=np.random.uniform(0.2, 0.4)
            )
            
            corona.add(streamer)
        
        return corona
    
    def _create_sunspots(self):
        """Create sunspots on the star's surface"""
        sunspots = VGroup()
        
        # Surface radius
        surface_radius = 2.4
        
        # Number of sunspots
        num_spots = 8
        
        # Create individual spots
        for _ in range(num_spots):
            # Position on the surface (mostly in mid-latitudes)
            r = surface_radius * np.random.uniform(0.5, 0.9)
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Size varies
            size = np.random.uniform(0.1, 0.25)
            
            # Create the dark center (umbra)
            umbra = Circle(
                radius=size * 0.6,
                fill_color="#000000",
                fill_opacity=0.8,
                stroke_width=0
            )
            
            # Create the lighter border (penumbra)
            penumbra = Circle(
                radius=size,
                fill_color="#8B4513",  # Dark brown
                fill_opacity=0.6,
                stroke_width=0
            )
            
            # Group and position
            spot = VGroup(penumbra, umbra)
            spot.move_to([x, y, 0])
            
            sunspots.add(spot)
        
        return sunspots
    
    def _create_flares(self):
        """Create solar flares and prominences"""
        flares = VGroup()
        
        # Surface radius
        surface_radius = 2.4
        
        # Create a few major flares
        num_flares = 5
        for _ in range(num_flares):
            # Position on the surface
            theta = np.random.uniform(0, TAU)
            x_start = surface_radius * np.cos(theta)
            y_start = surface_radius * np.sin(theta)
            
            # Flare characteristics
            height = np.random.uniform(0.3, 0.8)
            width_start = np.random.uniform(0.05, 0.15)
            width_end = width_start * np.random.uniform(0.3, 0.8)  # Tapers off
            
            # Create the flare shape (curving arc)
            # Create control points for the Bezier curve
            # Normal direction from the surface
            normal_x = np.cos(theta)
            normal_y = np.sin(theta)
            
            # Tangent direction (perpendicular to normal)
            tangent_x = -np.sin(theta)
            tangent_y = np.cos(theta)
            
            # Add some randomness to the curve
            curve_factor = np.random.uniform(0.3, 0.7) * np.random.choice([-1, 1])
            
            # End point
            end_radius = surface_radius + height * 0.7
            end_angle = theta + curve_factor * 0.3
            x_end = end_radius * np.cos(end_angle)
            y_end = end_radius * np.sin(end_angle)
            
            # Control points
            ctrl1_x = x_start + height * 0.3 * normal_x + curve_factor * width_start * tangent_x
            ctrl1_y = y_start + height * 0.3 * normal_y + curve_factor * width_start * tangent_y
            
            ctrl2_x = x_end - height * 0.3 * np.cos(end_angle) + curve_factor * width_end * tangent_x
            ctrl2_y = y_end - height * 0.3 * np.sin(end_angle) + curve_factor * width_end * tangent_y
            
            # Create the flare curve
            flare_curve = CubicBezier(
                start=[x_start, y_start, 0],
                h1=[ctrl1_x, ctrl1_y, 0],
                h2=[ctrl2_x, ctrl2_y, 0],
                end=[x_end, y_end, 0],
                stroke_color="#FF4500",  # Orange-red
                stroke_width=width_start * 100,  # Scale up to be visible
                stroke_opacity=0.7
            )
            
            flares.add(flare_curve)
        
        # Create smaller prominences
        num_prominences = 12
        for _ in range(num_prominences):
            # Position on the surface
            theta = np.random.uniform(0, TAU)
            x_start = surface_radius * np.cos(theta)
            y_start = surface_radius * np.sin(theta)
            
            # Normal direction from the surface
            normal_x = np.cos(theta)
            normal_y = np.sin(theta)
            
            # Prominence characteristics (smaller than flares)
            height = np.random.uniform(0.1, 0.3)
            width = np.random.uniform(0.02, 0.08)
            
            # End point (loop back to the surface)
            loop_width = np.random.uniform(0.1, 0.4)
            loop_angle = theta + loop_width / surface_radius
            x_end = surface_radius * np.cos(loop_angle)
            y_end = surface_radius * np.sin(loop_angle)
            
            # Control point (loop peak)
            ctrl_radius = surface_radius + height
            ctrl_angle = (theta + loop_angle) / 2
            x_ctrl = ctrl_radius * np.cos(ctrl_angle)
            y_ctrl = ctrl_radius * np.sin(ctrl_angle)
            
            # Create the prominence loop
            prominence = QuadraticBezier(
                start=[x_start, y_start, 0],
                control=[x_ctrl, y_ctrl, 0],
                end=[x_end, y_end, 0],
                stroke_color="#FF6347",  # Tomato
                stroke_width=width * 100,  # Scale up to be visible
                stroke_opacity=0.5
            )
            
            flares.add(prominence)
        
        return flares