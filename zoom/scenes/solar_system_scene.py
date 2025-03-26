"""
Solar System scene implementation for NPQG Zoom Animation
Represents a solar system at the 10^11 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class SolarSystemScene(ZoomableScene):
    """Scene representing a solar system at 10^11 m scale"""
    
    def __init__(self, config, scale_value=11):
        """
        Initialize the solar system scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to 11 (10^11 m)
        """
        super().__init__(config, scale_value, "Solar System")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Solar System scene elements")
        elements = []
        
        try:
            # Create the main solar system boundary using the base class method
            # This will automatically load custom images if available
            system_radius = 3
            system = self.create_object(
                "Solar System",
                [0, 0, 0],
                system_radius
            )
            elements.append(system)
            
            # Only add these additional elements if we're not using a custom image
            # or if they should appear alongside the custom image
            has_custom_image = False
            for submob in system.submobjects:
                if isinstance(submob, ImageMobject):
                    has_custom_image = True
                    break
                    
            if not self.use_custom_images or not has_custom_image:
                # Create the central star
                try:
                    star = self._create_central_star()
                    elements.append(star)
                except Exception as e:
                    print(f"Error creating central star: {e}")
                
                # Create the planetary orbits and planets
                try:
                    planetary_system = self._create_planetary_system()
                    elements.append(planetary_system)
                except Exception as e:
                    print(f"Error creating planetary system: {e}")
                
                # Create the asteroid belt
                try:
                    asteroid_belt = self._create_asteroid_belt()
                    elements.append(asteroid_belt)
                except Exception as e:
                    print(f"Error creating asteroid belt: {e}")
                
                # Create the Kuiper Belt / Oort Cloud objects
                try:
                    outer_objects = self._create_outer_objects()
                    elements.append(outer_objects)
                except Exception as e:
                    print(f"Error creating outer objects: {e}")
            
            print(f"Created {len(elements)} Solar System scene elements")
            return elements
        except Exception as e:
            print(f"Error in SolarSystem.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_central_star(self):
        """Create the central star of the solar system"""
        # Create a bright yellow-white star at the center
        star_group = VGroup()
        
        # Core of the star
        star_core = Circle(
            radius=0.25,
            fill_color="#FFFFFF",
            fill_opacity=1.0,
            stroke_width=0
        )
        
        # Outer layer with gradient
        star_outer = Circle(
            radius=0.35,
            fill_color="#FFD700",  # Gold
            fill_opacity=0.8,
            stroke_width=0
        )
        
        # Corona/Atmosphere
        star_corona = Circle(
            radius=0.45,
            fill_color="#FFA500",  # Orange
            fill_opacity=0.3,
            stroke_width=0
        )
        
        # Star glow
        star_glow = Circle(
            radius=0.6,
            fill_opacity=0,
            stroke_width=10,
            stroke_color="#FFFF00",
            stroke_opacity=0.2
        )
        
        # Add solar flares/prominences
        flares = VGroup()
        num_flares = 8
        for i in range(num_flares):
            # Position around the star
            angle = i * TAU / num_flares
            # Vary the size and shape
            size = np.random.uniform(0.05, 0.15)
            
            # Create a triangular flare
            flare = Triangle(
                fill_color="#FFA500",
                fill_opacity=0.6,
                stroke_width=0
            )
            flare.scale(size)
            
            # Position and rotate the flare
            radius = 0.35  # Star radius
            flare.move_to(radius * np.array([np.cos(angle), np.sin(angle), 0]))
            flare.rotate(angle + PI)  # Point outward
            
            flares.add(flare)
        
        star_group.add(star_outer, star_core, star_corona, star_glow, flares)
        return star_group
    
    def _create_planetary_system(self):
        """Create the planets and their orbits"""
        planetary_system = VGroup()
        
        # Define planets with relative sizes and colors
        planets = [
            {"name": "Mercury", "radius": 0.03, "distance": 0.7, "color": "#A9A9A9", "orbital_speed": 4.1},
            {"name": "Venus", "radius": 0.05, "distance": 1.0, "color": "#E0B58C", "orbital_speed": 3.0},
            {"name": "Earth", "radius": 0.055, "distance": 1.3, "color": "#1E90FF", "orbital_speed": 2.5},
            {"name": "Mars", "radius": 0.04, "distance": 1.6, "color": "#FF4500", "orbital_speed": 2.0},
            {"name": "Jupiter", "radius": 0.15, "distance": 2.0, "color": "#DAA06D", "orbital_speed": 1.3},
            {"name": "Saturn", "radius": 0.12, "distance": 2.35, "color": "#E3CF9C", "orbital_speed": 1.0, "has_rings": True},
            {"name": "Uranus", "radius": 0.08, "distance": 2.6, "color": "#87CEEB", "orbital_speed": 0.7},
            {"name": "Neptune", "radius": 0.08, "distance": 2.8, "color": "#0000CD", "orbital_speed": 0.5}
        ]
        
        # Create orbits and planets
        for planet_data in planets:
            # Create the orbit path
            orbit = Circle(
                radius=planet_data["distance"],
                stroke_color=WHITE,
                stroke_opacity=0.3,
                stroke_width=1,
                fill_opacity=0
            )
            
            # Create the planet
            planet = Circle(
                radius=planet_data["radius"],
                fill_color=planet_data["color"],
                fill_opacity=1.0,
                stroke_width=0
            )
            
            # Position the planet on its orbit
            # Random starting angle
            angle = np.random.uniform(0, TAU)
            x = planet_data["distance"] * np.cos(angle)
            y = planet_data["distance"] * np.sin(angle)
            planet.move_to([x, y, 0])
            
            # Add rings for Saturn
            if planet_data.get("has_rings", False):
                rings = self._create_saturn_rings(planet_data["radius"], [x, y, 0])
                planetary_system.add(rings)
            
            # Add moons for larger planets
            if planet_data["radius"] > 0.07:
                num_moons = int(planet_data["radius"] * 50)  # More moons for larger planets
                moons = self._create_moons(planet_data["radius"], [x, y, 0], num_moons)
                planetary_system.add(moons)
            
            planetary_system.add(orbit, planet)
        
        return planetary_system
    
    def _create_saturn_rings(self, planet_radius, planet_position):
        """Create rings for Saturn"""
        rings = VGroup()
        
        # Create multiple concentric rings
        inner_radius = planet_radius * 1.2
        outer_radius = planet_radius * 2.2
        num_rings = 8
        
        for i in range(num_rings):
            ring_radius = inner_radius + (outer_radius - inner_radius) * i / (num_rings - 1)
            ring_thickness = 0.01 * (1 + 0.5 * np.sin(i * PI / num_rings))  # Vary thickness
            
            ring = Circle(
                radius=ring_radius,
                stroke_width=ring_thickness * 100,  # Scale up to be visible
                stroke_color="#E3CF9C",
                stroke_opacity=0.3 + 0.4 * np.sin(i * PI / num_rings),  # Vary opacity
                fill_opacity=0
            )
            
            # Position at the planet and add perspective (tilt)
            ring.move_to(planet_position)
            ring.stretch(0.3, 1)  # Squash vertically for perspective
            
            rings.add(ring)
        
        return rings
    
    def _create_moons(self, planet_radius, planet_position, num_moons):
        """Create moons orbiting a planet"""
        moons = VGroup()
        
        for i in range(num_moons):
            # Moon orbit radius
            orbit_radius = planet_radius * (1.5 + np.random.uniform(0, 1.0))
            
            # Moon size (smaller than the planet)
            moon_radius = planet_radius * np.random.uniform(0.1, 0.2)
            
            # Random position on the orbit
            angle = np.random.uniform(0, TAU)
            moon_x = planet_position[0] + orbit_radius * np.cos(angle)
            moon_y = planet_position[1] + orbit_radius * np.sin(angle)
            
            # Create the moon
            moon = Circle(
                radius=moon_radius,
                fill_color="#D3D3D3",  # Light gray
                fill_opacity=1.0,
                stroke_width=0
            )
            moon.move_to([moon_x, moon_y, 0])
            
            # Only show moons if they're within the scene boundary
            distance_from_center = np.sqrt(moon_x**2 + moon_y**2)
            if distance_from_center < 2.9:  # Keep within scene boundary
                moons.add(moon)
        
        return moons
    
    def _create_asteroid_belt(self):
        """Create the asteroid belt between inner and outer planets"""
        asteroid_belt = VGroup()
        
        # Position of the asteroid belt
        inner_radius = 1.7
        outer_radius = 1.9
        
        # Create individual asteroids
        num_asteroids = 150
        for _ in range(num_asteroids):
            # Random position in the belt
            radius = np.random.uniform(inner_radius, outer_radius)
            angle = np.random.uniform(0, TAU)
            
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create the asteroid (small irregular shape)
            size = np.random.uniform(0.005, 0.015)
            
            # Use a small dot for simplicity
            asteroid = Dot(
                point=[x, y, 0],
                radius=size,
                color="#8B7E66",  # Brownish-gray
                fill_opacity=np.random.uniform(0.5, 1.0)
            )
            
            asteroid_belt.add(asteroid)
        
        return asteroid_belt
    
    def _create_outer_objects(self):
        """Create Kuiper Belt / Oort Cloud objects"""
        outer_objects = VGroup()
        
        # Create a diffuse cloud of distant objects
        num_objects = 100
        for _ in range(num_objects):
            # Random position in outer solar system
            # Use a distribution that puts more objects at the edge
            radius = 2.7 + np.random.power(2) * 0.2  # Power function concentrates points
            angle = np.random.uniform(0, TAU)
            
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create the object (very small)
            size = np.random.uniform(0.003, 0.01)
            
            # Vary colors slightly
            color = random.choice(["#B0C4DE", "#D3D3D3", "#F0F8FF"])  # Light blues and grays
            
            obj = Dot(
                point=[x, y, 0],
                radius=size,
                color=color,
                fill_opacity=np.random.uniform(0.2, 0.6)
            )
            
            outer_objects.add(obj)
        
        return outer_objects