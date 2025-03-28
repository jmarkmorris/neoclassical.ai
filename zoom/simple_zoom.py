#!/usr/bin/env python3
"""
Simple direct implementation of NPQG Universe Zoom Animation
This version uses Manim directly without the complex architecture
"""

from manim import *

# Constants
INDIGO = "#4B0082"  # Purple color as requested

class SimpleZoomScene(Scene):
    def construct(self):
        # Set the background color to purple (indigo)
        self.camera.background_color = INDIGO
        
        # Create a background for the scene
        background = Rectangle(
            width=config.frame_width * 2,
            height=config.frame_height * 2,
            color=INDIGO,
            fill_color=INDIGO,
            fill_opacity=1.0,
            stroke_width=0
        )
        self.add(background)
        
        # Create the universe scale scene
        universe_scale = Text("10^26 m", font="Arial", font_size=24)
        universe_scale.to_corner(UP + RIGHT, buff=0.5)
        
        universe_circle = Circle(radius=3, stroke_color=WHITE)
        universe_label = Text("Observable Universe", font="Arial", font_size=24)
        universe = VGroup(universe_circle, universe_label)
        
        # Create the galaxy cluster scale scene
        galaxy_scale = Text("10^23 m", font="Arial", font_size=24)
        galaxy_scale.to_corner(UP + RIGHT, buff=0.5)
        
        galaxy_circle = Circle(radius=3, stroke_color=WHITE)
        galaxy_label = Text("Galaxy Cluster", font="Arial", font_size=24)
        galaxy = VGroup(galaxy_circle, galaxy_label)
        
        # Start with universe scene
        self.add(universe_scale, universe)
        
        # Wait for a moment
        self.wait(1)
        
        # Create a camera_group that we'll use for zooming
        camera_group = VGroup()
        self.add(camera_group)
        
        # Zoom in transition (instead of using camera.frame which may not exist)
        self.play(
            # Make universe objects larger (simulating zoom in)
            universe.animate.scale(10),
            universe_scale.animate.scale(0).shift(DOWN * 10),  # Make scale disappear
            
            # Show galaxy scene
            FadeIn(galaxy_scale),
            FadeIn(galaxy),
            
            run_time=5
        )
        
        # Remove universe objects as they're now too large
        self.remove(universe, universe_scale)
        
        # Wait for a moment
        self.wait(1)
        
        # Zoom out transition
        self.play(
            # Make galaxy objects smaller (simulating zoom out)
            galaxy.animate.scale(0.1),
            galaxy_scale.animate.scale(0).shift(DOWN * 10),  # Make scale disappear
            
            # Show universe scene
            FadeIn(universe_scale),
            FadeIn(universe.scale(0.1)),  # Need to scale it back down
            
            run_time=5
        )
        
        # Remove galaxy objects
        self.remove(galaxy, galaxy_scale)
        
        # Wait for a moment
        self.wait(1)


if __name__ == "__main__":
    # This script can be run directly with:
    # manim -pql simple_zoom.py SimpleZoomScene
    pass