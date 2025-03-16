import json
import sys
import os
import math
import numpy as np
from manim import *
from typing import Dict, Any, List, Tuple

# Use consistent Vector3D class for compatibility
class Vector3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, (list, tuple)) and len(x) >= 3:
            self.x, self.y, self.z = float(x[0]), float(x[1]), float(x[2])
        else:
            self.x, self.y, self.z = float(x), float(y), float(z)
    
    def __add__(self, other):
        if isinstance(other, Vector3D):
            return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, (list, tuple)) and len(other) >= 3:
            return Vector3D(self.x + other[0], self.y + other[1], self.z + other[2])
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vector3D):
            return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, (list, tuple)) and len(other) >= 3:
            return Vector3D(self.x - other[0], self.y - other[1], self.z - other[2])
        return NotImplemented
        
    def norm(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def tolist(self):
        return [self.x, self.y, self.z]


class TracingTail(VGroup):
    """A VGroup that traces the path of a moving object with smooth fading trail"""
    
    def __init__(self, mobject, max_points=250, stroke_width=1, stroke_color=WHITE, **kwargs):
        super().__init__(**kwargs)
        self.mobject = mobject
        self.max_points = max_points
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        
        # Store state
        self.points = []
        
        # Add updater that runs on each frame
        self.add_updater(self._update_path)
    
    def _update_path(self, mobject, dt):
        """Update the trailing path for each frame"""
        # Get current position of the mobject
        current_point = self.mobject.get_center()
        
        # Add the current point to our path
        self.points.append(current_point.copy())  # Use copy to prevent reference issues
        
        # Limit the number of points in the path history
        if len(self.points) > self.max_points:
            self.points.pop(0)
        
        # Clear all previous submobjects
        self.submobjects = []
        
        # If we have at least 2 points, draw line segments
        if len(self.points) >= 2:
            # Create individual line segments with varying opacity
            for i in range(len(self.points) - 1):
                # Calculate opacity based on position in the path
                # First segments (oldest) should be nearly transparent
                # Last segments (newest) should be most visible
                opacity = i / (len(self.points) - 1)  # 0.0 to 1.0
                
                # Create line segment
                line = Line(
                    start=self.points[i],
                    end=self.points[i + 1],
                    stroke_width=self.stroke_width,
                    stroke_color=self.stroke_color,
                    stroke_opacity=opacity  # Apply calculated opacity
                )
                
                # Add line to group
                self.add(line)


class PotentialVisualization(ThreeDScene):
    """Enhanced visualization for point potentials incorporating the best from both approaches"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load simulation data from default file or environment variable
        results_file = os.environ.get("SIMULATION_RESULTS", "simulation_results.json")
        print(f"Loading simulation data from: {results_file}")
        self.simulation_data = self._load_simulation_results(results_file)
        self.config = self.simulation_data.get("config", {})
        self.colors = self._setup_colors()
        
        # Get visualization parameters
        viz_config = self.config.get("visualization", {})
        self.marker_size = viz_config.get("marker_size", 0.04)
        self.use_dot3d = viz_config.get("use_dot3d", True)
        self.tracer_config = viz_config.get("tracer", {})
        self.sim_to_manim_ratio = viz_config.get("sim_to_manim_ratio", 5)
        
        # Get scaling configuration
        scaling_config = viz_config.get("scaling", {})
        self.scaling_enabled = scaling_config.get("enabled", True)
        self.base_scale = scaling_config.get("initial_scale", 1.0)
        self.max_display_limit = 5.0
        self.min_display_limit = 2.0
        
        # Initialize scale history for smoothing
        self.last_scale = self.base_scale
        self.scale_history = [self.base_scale] * 5
        self.scale_stability_threshold = 0.2
    
    def _load_simulation_results(self, file_path):
        """Load simulation results from a JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _setup_colors(self):
        """Setup colors from config or use defaults"""
        viz_config = self.config.get("visualization", {})
        colors = viz_config.get("colors", {})
        
        return {
            "background": colors.get("background", "#4B0082"),
            "positive": PURE_RED,  # Use PURE_RED as requested
            "negative": PURE_BLUE,  # Use PURE_BLUE as requested
            "tracer": colors.get("tracer", "#FFFFFF")
        }
    
    def _get_particle_color(self, charge):
        """Get the color for a particle based on its charge"""
        return self.colors["positive"] if charge > 0 else self.colors["negative"]
    
    def _calculate_scale_factor(self, all_positions):
        """Calculate appropriate scale factor based on particle positions"""
        # If scaling is disabled, return the initial scale factor
        if not self.scaling_enabled:
            return self.base_scale
            
        # Calculate the maximum absolute coordinate
        max_coord = 0
        for pos in all_positions:
            max_abs = max(abs(p) for p in pos)
            if max_abs > max_coord:
                max_coord = max_abs
        
        # Calculate the range between particles
        min_pos = [float('inf'), float('inf'), float('inf')]
        max_pos = [float('-inf'), float('-inf'), float('-inf')]
        
        for pos in all_positions:
            for dim in range(3):
                if dim < len(pos):
                    min_pos[dim] = min(min_pos[dim], pos[dim])
                    max_pos[dim] = max(max_pos[dim], pos[dim])
        
        # Calculate maximum range across dimensions
        ranges = [max_pos[dim] - min_pos[dim] for dim in range(3) 
                  if min_pos[dim] != float('inf') and max_pos[dim] != float('-inf')]
        max_range = max(ranges) if ranges else 0
        
        # Determine if we need to scale down or up
        need_scale_down = max_coord * self.base_scale > self.max_display_limit
        need_scale_up = max_range > 0 and max_range * self.base_scale < self.min_display_limit
        
        # Calculate scale factors
        scale_down_factor = self.max_display_limit / max_coord if need_scale_down else self.base_scale
        scale_up_factor = self.min_display_limit / max_range if need_scale_up else self.base_scale
        scale_up_factor = min(scale_up_factor, self.base_scale * 2.0)  # Limit max zoom
        
        # Determine suggested scale
        suggested_scale = self.base_scale
        if need_scale_down:
            suggested_scale = scale_down_factor
        elif need_scale_up:
            suggested_scale = scale_up_factor
        
        # Apply stability with smoothing
        scale_diff = abs(suggested_scale - self.last_scale)
        if scale_diff > self.scale_stability_threshold:
            # Update scale history
            self.scale_history.pop(0)
            self.scale_history.append(suggested_scale)
            
            # Apply smoothing with moving average
            current_scale = sum(self.scale_history) / len(self.scale_history)
            self.last_scale = current_scale
        else:
            current_scale = self.last_scale
        
        # Debug info
        print(f"max_coord={max_coord:.2f}, max_range={max_range:.2f}, scale={current_scale:.2f}")
        
        return current_scale
    
    def construct(self):
        # Set up the scene
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.camera.background_color = self.colors["background"]
        
        # Add axes for reference
        axes = ThreeDAxes()
        self.add(axes)
        
        # Create scale indicator as fixed overlay
        # We'll always show the scale, even if scaling is disabled
        scale_indicator = Text(f"Scale: {self.base_scale:.2f}", font_size=24, color=WHITE)
        scale_indicator.to_corner(UR, buff=0.5)
        self.add_fixed_in_frame_mobjects(scale_indicator)
        
        # Extract particle data and create representations
        particle_data = self.simulation_data["particle_data"]
        times = self.simulation_data["times"]
        particles = []
        tracers = {}
        
        # Process particles
        for p_id_str, p_data in particle_data.items():
            positions = p_data["positions"]
            
            # Determine color based on charge
            particles_config = self.config.get("simulation", {}).get("particles", [])
            charge = 0
            
            for p_cfg in particles_config:
                if str(p_cfg.get("id")) == p_id_str:
                    charge = p_cfg.get("charge", 0)
                    break
            
            # Get color and create particle
            color = self._get_particle_color(charge)
            
            # Create particle representation based on configuration
            if self.use_dot3d:
                particle = Dot3D(radius=self.marker_size, color=color)
            else:
                particle = Sphere(radius=self.marker_size, color=color)
            
            # Initial positioning
            initial_pos = [self.base_scale * p for p in positions[0]]
            particle.move_to(initial_pos)
            
            # Add tracer if enabled first (so particle will be on top)
            if self.tracer_config.get("enabled", True):
                # Create tracer with basic parameters - individual line segments
                tracer = TracingTail(
                    particle,
                    max_points=self.tracer_config.get("history_length", 100),
                    stroke_color=self.colors["tracer"],
                    stroke_width=2
                )
                self.add(tracer)
                tracers[p_id_str] = tracer
            
            # Add particle AFTER tracer so it appears on top
            self.add(particle)
            particles.append((particle, positions))
        
        # Animate the simulation
        sampling_rate = self.sim_to_manim_ratio  # Use the exact sim_to_manim_ratio for smoother animations
        
        for i in range(0, len(times), sampling_rate):
            if i >= len(times):
                break
            
            # Determine appropriate scale
            all_positions = []
            for _, pos_data in particle_data.items():
                if i < len(pos_data["positions"]):
                    all_positions.append(pos_data["positions"][i])
            
            # Calculate scale factor with smoothing
            current_scale = self._calculate_scale_factor(all_positions)
            
            # Move particles with the adjusted scale
            animations = []
            for particle, positions in particles:
                if i < len(positions):
                    pos = positions[i]
                    new_pos = [current_scale * p for p in pos]
                    # Use a smoother animation with a shorter run time to reduce jumpiness
                    animations.append(particle.animate.move_to(new_pos))
            
            if animations:
                # Use even shorter run time and linear rate for smoother motion
                self.play(*animations, run_time=0.05, rate_func=linear)
                
                # Always update scale indicator for each frame
                new_scale_text = Text(f"Scale: {current_scale:.2f}", font_size=24, color=WHITE)
                new_scale_text.to_corner(UR, buff=0.5)
                
                # Remove old scale indicator and add the new one
                self.remove(scale_indicator)
                scale_indicator = new_scale_text
                self.add_fixed_in_frame_mobjects(scale_indicator)
        
        # Final pause
        self.wait(2)


if __name__ == "__main__":
    try:
        # When run directly, render the visualization
        print("Rendering visualization...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)