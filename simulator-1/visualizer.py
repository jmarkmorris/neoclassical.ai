import json
import sys
import os
import math
from manim import *
from typing import Dict, Any, List, Tuple

# Use native Python arrays instead of NumPy for compatibility
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
    
    def tolist(self):
        return [self.x, self.y, self.z]


class CoordinateMapper:
    """Maps simulation coordinates to Manim coordinates"""
    
    def __init__(self, scale_factor=1.0, translation=[0, 0, 0], 
                 rotation_matrix=None):
        self.scale_factor = scale_factor
        self.translation = translation
        
        # Default identity rotation matrix
        if rotation_matrix is None:
            self.rotation_matrix = [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]
            ]
        else:
            self.rotation_matrix = rotation_matrix
    
    def map_to_manim(self, sim_coords):
        """Map simulation coordinates to Manim coordinates"""
        # Convert to list if it's a Vector3D
        if hasattr(sim_coords, 'tolist'):
            sim_coords = sim_coords.tolist()
            
        # Apply rotation (using a simple implementation)
        rotated = [0, 0, 0]
        for i in range(3):
            for j in range(3):
                rotated[i] += self.rotation_matrix[i][j] * sim_coords[j]
        
        # Apply scaling and translation
        manim_coords = [
            self.scale_factor * rotated[0] + self.translation[0],
            self.scale_factor * rotated[1] + self.translation[1],
            self.scale_factor * rotated[2] + self.translation[2]
        ]
        
        return manim_coords
    
    def update_params(self, scale_factor=None, translation=None, rotation_matrix=None):
        """Update mapping parameters"""
        if scale_factor is not None:
            self.scale_factor = scale_factor
        if translation is not None:
            self.translation = translation
        if rotation_matrix is not None:
            self.rotation_matrix = rotation_matrix


class ParticleAnimation(ThreeDScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load simulation data from environment variable or default file
        results_file = os.environ.get("SIMULATION_RESULTS", "simulation_results.json")
        print(f"Loading simulation data from: {results_file}")
        self.simulation_data = load_simulation_results(results_file)
        self.config = self.simulation_data.get("config", {})
        self.colors = self._setup_colors()
        self.marker_size = self.config.get("visualization", {}).get("marker_size", 0.1)
        self.tracer_config = self.config.get("visualization", {}).get("tracer", {})
        self.sim_to_manim_ratio = self.config.get("visualization", {}).get("sim_to_manim_ratio", 10)
        # Use a larger scale factor to make particles more visible
        self.mapper = CoordinateMapper(scale_factor=3.0)
    
    def _setup_colors(self):
        """Setup colors from config or use defaults"""
        viz_config = self.config.get("visualization", {})
        colors = viz_config.get("colors", {})
        
        return {
            "background": colors.get("background", "#4B0082"),
            "positive": colors.get("positive", "#FF0000"),
            "negative": colors.get("negative", "#0000FF"),
            "tracer": colors.get("tracer", "#FFFFFF")
        }
    
    def _get_particle_color(self, charge):
        """Get the color for a particle based on its charge"""
        if charge > 0:
            return self.colors["positive"]
        else:
            return self.colors["negative"]
    
    def construct(self):
        # Set up the scene
        self.camera.background_color = self.colors["background"]
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES, zoom=0.8)
        
        # Add debug info
        print(f"Simulation data keys: {self.simulation_data.keys()}")
        
        # Extract particle data
        particle_data = self.simulation_data["particle_data"]
        times = self.simulation_data["times"]
        
        print(f"Particle IDs: {list(particle_data.keys())}")
        print(f"Number of time steps: {len(times)}")
        
        # Create particles with larger size for visibility
        particles = {}
        tracers = {}
        
        # Add axes for reference
        axes = ThreeDAxes()
        self.add(axes)
        
        for p_id_str, data in particle_data.items():
            p_id = int(p_id_str)
            
            # Get charge from config
            charge = next((p["charge"] for p in self.config["simulation"]["particles"] 
                          if p["id"] == p_id), 1)  # Default to positive if not found
            
            color = self._get_particle_color(charge)
            
            # Get particle size from config
            viz_config = self.config.get("visualization", {})
            particle_size = viz_config.get('marker_size', 0.04)
            
            # Create particle
            initial_pos = self.mapper.map_to_manim(data["positions"][0])
            print(f"Particle {p_id} initial position: {initial_pos}")
            
            # Make sure the initial position is a 3D point
            if len(initial_pos) != 3:
                print(f"Warning: Initial position for particle {p_id} is not 3D: {initial_pos}")
                initial_pos = np.array([0, 0, 0])
            
            particle = Sphere(radius=particle_size, color=color).move_to(initial_pos)
            self.add(particle)
            particles[p_id_str] = particle
            
            # Create tracer if enabled
            if self.tracer_config.get("enabled", True):
                tracer = TracingTail(
                    particle,
                    max_points=self.tracer_config.get("history_length", 100),
                    stroke_color=self.colors["tracer"],
                    stroke_width=3,  # Thicker for visibility
                    stroke_opacity=0.8 if not self.tracer_config.get("fade", True) else None
                )
                self.add(tracer)
                tracers[p_id_str] = tracer
        
        # Wait a bit before starting animation
        self.wait(0.5)
        
        # Animate particles
        frame_duration = 1/30  # 30 FPS default
        
        for i in range(0, len(times), self.sim_to_manim_ratio):
            if i >= len(times):
                break
                
            # Create animations for all particles
            animations = []
            
            for p_id_str, particle in particles.items():
                if i < len(particle_data[p_id_str]["positions"]):
                    pos_data = particle_data[p_id_str]["positions"][i]
                    
                    # Convert to numpy array if it's a list
                    if isinstance(pos_data, list):
                        pos_data = np.array(pos_data)
                    
                    # Map simulation coordinates to Manim coordinates
                    manim_pos = self.mapper.map_to_manim(pos_data)
                    
                    # Add animation to move the particle
                    animations.append(particle.animate.move_to(manim_pos))
            
            # Play all animations simultaneously
            if animations:
                self.play(*animations, run_time=frame_duration)
        
        # Wait at the end
        self.wait(1)


class TracingTail(VGroup):
    """A VGroup that traces the path of a moving object"""
    
    def __init__(self, mobject, max_points=100, stroke_width=2, stroke_color=WHITE, 
                 stroke_opacity=None, **kwargs):
        super().__init__(**kwargs)
        self.mobject = mobject
        self.max_points = max_points
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        
        self.points = []
        self.lines = []
        self.add_updater(self._update_path)
    
    def _update_path(self, mobject, dt):
        point = self.mobject.get_center()
        self.points.append(point)
        
        # Limit number of points
        if len(self.points) > self.max_points:
            self.points.pop(0)
        
        # Remove all submobjects (lines)
        self.submobjects = []
        
        # Draw new lines
        if len(self.points) > 1:
            if self.stroke_opacity is None:
                # Create gradient opacity
                opacities = np.linspace(0, 1, len(self.points))
                for i in range(len(self.points) - 1):
                    line = Line(
                        self.points[i], 
                        self.points[i + 1],
                        stroke_width=self.stroke_width,
                        stroke_color=self.stroke_color,
                        stroke_opacity=opacities[i]
                    )
                    self.add(line)
            else:
                # Use constant opacity
                path = VMobject()
                path.set_points_as_corners(self.points)
                path.set_stroke(
                    color=self.stroke_color,
                    width=self.stroke_width,
                    opacity=self.stroke_opacity
                )
                self.add(path)


def load_simulation_results(file_path):
    """Load simulation results from a JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    try:
        # When run directly, the ParticleAnimation class will be instantiated 
        # by the Manim CLI, which will handle rendering
        pass
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)