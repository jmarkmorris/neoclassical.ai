"""
Point Potential scene implementation for NPQG Zoom Animation
Represents point potentials at the 10^-60 m scale
"""

import random
import numpy as np
from manim import *
from scenes.base_scene import ZoomableScene

class PointPotentialScene(ZoomableScene):
    """Scene representing point potentials at 10^-60 m scale"""
    
    def __init__(self, config, scale_value=-60):
        """
        Initialize the point potential scene
        
        Args:
            config (dict): The global configuration
            scale_value (float): The logarithmic scale value, defaults to -60 (10^-60 m)
        """
        super().__init__(config, scale_value, "Point Potential")
    
    def get_elements(self):
        """Get the scene-specific elements"""
        print("Creating Point Potential scene elements")
        elements = []
        
        try:
            # Create the main point potential boundary
            pp_radius = 3
            pp_circle = Circle(
                radius=pp_radius,
                stroke_color=WHITE,
                stroke_width=2,
                fill_opacity=0
            )
            pp_label = Text(
                "Point Potential",
                font_size=self.config["global_settings"].get("font_size", 24),
                color=WHITE
            )
            pp_boundary = VGroup(pp_circle, pp_label)
            elements.append(pp_boundary)
            
            # Create the point potential core
            try:
                pp_core = self._create_pp_core()
                elements.append(pp_core)
            except Exception as e:
                print(f"Error creating point potential core: {e}")
            
            # Create the wavefunction
            try:
                wavefunction = self._create_wavefunction()
                elements.append(wavefunction)
            except Exception as e:
                print(f"Error creating wavefunction: {e}")
            
            # Create quantum foam
            try:
                quantum_foam = self._create_quantum_foam()
                elements.append(quantum_foam)
            except Exception as e:
                print(f"Error creating quantum foam: {e}")
            
            # Create spacetime curvature
            try:
                spacetime_curvature = self._create_spacetime_curvature()
                elements.append(spacetime_curvature)
            except Exception as e:
                print(f"Error creating spacetime curvature: {e}")
            
            print(f"Created {len(elements)} Point Potential scene elements")
            return elements
        except Exception as e:
            print(f"Error in PointPotential.get_elements: {e}")
            # Return at least one element even if there's an error
            return [Circle(radius=3, stroke_color=WHITE)]
    
    def _create_pp_core(self):
        """Create the core of the point potential"""
        pp_core = VGroup()
        
        # Create a central point representing the point potential
        core = Dot(
            radius=0.05,
            color="#FFFFFF",
            fill_opacity=1.0
        )
        
        # Add a glow effect
        glow1 = Circle(
            radius=0.1,
            fill_color="#FFFFFF",
            fill_opacity=0.8,
            stroke_width=0
        )
        
        glow2 = Circle(
            radius=0.2,
            fill_color="#FFFFFF",
            fill_opacity=0.4,
            stroke_width=0
        )
        
        glow3 = Circle(
            radius=0.3,
            fill_color="#FFFFFF",
            fill_opacity=0.2,
            stroke_width=0
        )
        
        # Add quantum pulsing effect (concentric circles)
        pulses = VGroup()
        num_pulses = 5
        for i in range(num_pulses):
            pulse = Circle(
                radius=0.4 + 0.1 * i,
                stroke_color="#FFFFFF",
                stroke_width=2,
                stroke_opacity=0.5 - 0.1 * i,
                fill_opacity=0
            )
            pulses.add(pulse)
        
        pp_core.add(glow3, glow2, glow1, core, pulses)
        return pp_core
    
    def _create_wavefunction(self):
        """Create a visualization of the quantum wavefunction"""
        wavefunction = VGroup()
        
        # Create a radial wave pattern
        num_waves = 80
        wave_freq = 15  # Number of oscillations
        max_radius = 2.5
        
        wave_points = []
        
        for i in range(num_waves + 1):  # +1 to close the curve
            angle = i * TAU / num_waves
            
            # Oscillating radius (representing probability amplitude)
            # Using exponential decay with oscillation
            t = i / num_waves
            radius = max_radius * np.exp(-t * 3) * (0.5 + 0.5 * np.cos(wave_freq * t * TAU))
            
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            wave_points.append([x, y, 0])
        
        wave = VMobject()
        wave.set_points_smoothly([np.array(p) for p in wave_points])
        wave.set_stroke(color="#00FFFF", width=2, opacity=0.7)
        
        # Create radial lines representing probability flux
        num_lines = 16
        for i in range(num_lines):
            angle = i * TAU / num_lines
            
            # Vary the length for visual interest
            length = max_radius * (0.8 + 0.2 * np.cos(3 * angle))
            
            # Start near the center
            start_radius = 0.4
            start_x = start_radius * np.cos(angle)
            start_y = start_radius * np.sin(angle)
            
            # End at varying distances
            end_x = length * np.cos(angle)
            end_y = length * np.sin(angle)
            
            # Create the radial line with arrow
            line = Arrow(
                start=[start_x, start_y, 0],
                end=[end_x, end_y, 0],
                stroke_color="#00FFFF",
                stroke_width=1,
                stroke_opacity=0.5,
                buff=0
            )
            
            wavefunction.add(line)
        
        wavefunction.add(wave)
        return wavefunction
    
    def _create_quantum_foam(self):
        """Create a visualization of quantum foam"""
        foam = VGroup()
        
        # Create a background of random fluctuations
        num_fluctuations = 150
        
        for _ in range(num_fluctuations):
            # Random position (more concentrated near edges)
            r = np.random.uniform(1.0, 2.9)
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Random size and opacity
            size = np.random.uniform(0.01, 0.05)
            opacity = np.random.uniform(0.2, 0.8)
            
            # Create a small circle for each fluctuation
            fluctuation = Circle(
                radius=size,
                fill_color=random.choice(["#4B0082", "#8A2BE2", "#9370DB"]),  # Purple shades
                fill_opacity=opacity,
                stroke_width=0
            )
            fluctuation.move_to([x, y, 0])
            
            foam.add(fluctuation)
        
        # Create a few larger "bubble" fluctuations
        num_bubbles = 10
        for _ in range(num_bubbles):
            # Random position
            r = np.random.uniform(0.8, 2.5)
            theta = np.random.uniform(0, TAU)
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            
            # Size and opacity
            size = np.random.uniform(0.1, 0.3)
            opacity = np.random.uniform(0.1, 0.3)
            
            # Create a bubble
            bubble = Circle(
                radius=size,
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=0.5,
                fill_color="#4B0082",  # Indigo
                fill_opacity=opacity
            )
            bubble.move_to([x, y, 0])
            
            foam.add(bubble)
        
        return foam
    
    def _create_spacetime_curvature(self):
        """Create a visualization of spacetime curvature"""
        curvature = VGroup()
        
        # Create a grid representing spacetime
        grid_size = 5.0
        grid_step = 0.5
        grid_opacity = 0.3
        
        # Create grid lines
        for x in np.arange(-grid_size/2, grid_size/2 + grid_step/2, grid_step):
            # Vertical line
            v_line = Line(
                start=[x, -grid_size/2, 0],
                end=[x, grid_size/2, 0],
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=grid_opacity
            )
            
            # Horizontal line
            h_line = Line(
                start=[-grid_size/2, x, 0],
                end=[grid_size/2, x, 0],
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=grid_opacity
            )
            
            curvature.add(v_line, h_line)
        
        # Create a warped grid near the center to show spacetime curvature
        # Parameters for the curve
        center_influence = 1.5  # How much the center point affects the grid
        center_radius = 1.0  # Radius of influence
        
        # Create warped grid lines
        num_circles = 6
        for i in range(1, num_circles + 1):
            radius = i * center_radius / num_circles
            
            circle = Circle(
                radius=radius,
                stroke_color="#FFFFFF",
                stroke_width=1,
                stroke_opacity=grid_opacity + 0.1
            )
            
            # Scale the circle to show warping
            warp_factor = 1 - center_influence * np.exp(-radius / center_radius)
            circle.stretch(warp_factor, 1)  # Compress vertically
            
            curvature.add(circle)
        
        # Add radial lines
        num_radials = 12
        for i in range(num_radials):
            angle = i * TAU / num_radials
            
            # Create a curved line to represent warped spacetime
            curve_points = []
            
            for t in np.linspace(0, 1, 20):
                # Radius with warping
                r = t * 2.5
                
                # Apply warping - the more curved, the closer to the center
                warping = center_influence * np.exp(-r / center_radius)
                angle_adjusted = angle + warping * np.sin(angle)
                
                x = r * np.cos(angle_adjusted)
                y = r * np.sin(angle_adjusted) * (1 - warping * 0.5)  # Vertical compression
                
                curve_points.append([x, y, 0])
            
            # Create the curved line
            curve = VMobject()
            curve.set_points_smoothly([np.array(p) for p in curve_points])
            curve.set_stroke(color="#FFFFFF", width=1, opacity=grid_opacity + 0.1)
            
            curvature.add(curve)
        
        return curvature