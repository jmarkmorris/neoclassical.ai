import json
import sys
import os
import math
import numpy as np
from manim import *
from typing import Dict, Any, List, Tuple

# Default configuration values
DEFAULT_VISUALIZER_CONFIG = {
    "global": {
        "potential_velocity": 10.0     # Velocity of potential waves, used by both physics and visualization
    },
    "visualization": {
        "colors": {
            "background": "#4B0082",  # INDIGO
            "positive": "#FF0000",    # PURE_RED
            "negative": "#0000FF",    # PURE_BLUE
            "tracer_positive": "#FC6255",  # PALE RED
            "tracer_negative": "#58C4DD",  # PALE BLUE
            "tracer": "#FFFFFF",      # WHITE
            "history_lines": "#FFFFFF", # WHITE
            "potential_wave": "#FFFFFF"  # WHITE (for potential wave visualization)
        },
        "marker_size": 0.04,
        "use_dot3d": True,
        "tracer": {
            "enabled": True,
            "history_length": 12000,
            "stroke_width": 1,
            "add_spheres": False,
            "frames_between_trail_segments": 60,
            "sphere_radius": 0.02,
            "max_sphere_radius": 0.1,
            "use_particle_color": True  # If True, use particle-based colors, otherwise use common tracer color
        },
        "history_lines": {
            "enabled": False,          # Whether to show history lines
            "lines_per_relation": 3,   # Number of lines to show per particle pair
            "stroke_width": 1.0,       # Width of history lines
            "update_interval": 30      # Update connections every N simulation steps
        },
        "scaling": {
            "enabled": True,
            "initial_scale": 1.0,
            "max_display_limit": 5.0,
            "min_display_limit": 2.0,
            "scale_stability_threshold": 0.2
        },
        "sim_to_manim_ratio": 5,
        "manim_frame_rate": 60,
        "camera": {
            "phi": 75,  # in degrees
            "theta": 30 # in degrees
        }
    }
}

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
    """A VGroup that traces the path of a moving object"""
    
    def __init__(self, mobject, max_points=12000, stroke_width=1, stroke_color=WHITE, 
                 add_spheres=False, frames_between_spheres=60, 
                 sphere_radius=0.02, max_sphere_radius=0.1, **kwargs):
        super().__init__(**kwargs)
        self.mobject = mobject
        self.max_points = max_points
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        
        # Sphere tracer settings
        self.add_spheres = add_spheres
        self.frames_between_spheres = frames_between_spheres
        self.sphere_radius = sphere_radius
        self.max_sphere_radius = max_sphere_radius
        self.frame_counter = 0
        
        # Store state
        self.points = []
        self.sphere_positions = []
        
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
        
        # Update sphere positions if needed
        if self.add_spheres:
            self.frame_counter += 1
            if self.frame_counter >= self.frames_between_spheres:
                self.frame_counter = 0
                self.sphere_positions.append(current_point.copy())
                # Limit number of spheres
                if len(self.sphere_positions) > self.max_points // self.frames_between_spheres:
                    self.sphere_positions.pop(0)
        
        # Clear all previous submobjects
        self.submobjects = []
        
        # If we have at least 2 points, draw line segments
        if len(self.points) >= 2:
            # Create individual line segments
            for i in range(len(self.points) - 1):
                # Create line segment
                line = Line(
                    start=self.points[i],
                    end=self.points[i + 1],
                    stroke_width=self.stroke_width,
                    stroke_color=self.stroke_color
                )
                
                # Add line to group
                self.add(line)
                
        # Add sphere tracers if enabled
        if self.add_spheres and self.sphere_positions:
            for i, pos in enumerate(self.sphere_positions):
                # Calculate opacity for spheres (older ones are more transparent)
                opacity = (i + 1) / len(self.sphere_positions) * 0.7 + 0.1  # Range from 0.1 to 0.8
                
                # Create sphere with decreasing size for older points
                radius = max(self.sphere_radius * (i + 1) / len(self.sphere_positions), 
                            self.sphere_radius / 3)
                radius = min(radius, self.max_sphere_radius)
                
                dot = Dot3D(
                    point=pos,
                    radius=radius,
                    color=self.stroke_color,
                    opacity=opacity,
                    resolution=(32, 16)
                )
                self.add(dot)


class PotentialVisualization(ThreeDScene):
    """Enhanced visualization for point potentials incorporating the best from both approaches"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load simulation data from default file or environment variable
        results_file = os.environ.get("SIMULATION_RESULTS", "simulation_results.json")
        print(f"Loading simulation data from: {results_file}")
        self.simulation_data = self._load_simulation_results(results_file)
        self.config = self._prepare_config()
        self.colors = self._setup_colors()
        
        # Custom output name is handled by the command line parameter
        # We don't need to modify file_writer directly as it causes errors
        output_name = os.environ.get("VISUALIZATION_OUTPUT_NAME")
        if output_name:
            print(f"Using custom output name: {output_name}")
        
        # Extract configuration parameters
        viz_config = self.config["visualization"]
        self.marker_size = viz_config["marker_size"]
        self.use_dot3d = viz_config["use_dot3d"]
        self.tracer_config = viz_config["tracer"]
        self.sim_to_manim_ratio = viz_config["sim_to_manim_ratio"]
        
        # Extract history lines configuration
        self.history_lines_config = viz_config.get("history_lines", {
            "enabled": False,
            "interval": 20,
            "stroke_width": 1.0,
            "max_lines": 500
        })
        
        # Extract scaling configuration
        scaling_config = viz_config["scaling"]
        self.scaling_enabled = scaling_config["enabled"]
        self.base_scale = scaling_config["initial_scale"]
        self.max_display_limit = scaling_config["max_display_limit"]
        self.min_display_limit = scaling_config["min_display_limit"]
        self.scale_stability_threshold = scaling_config["scale_stability_threshold"]
        
        # Initialize scale history for smoothing
        self.last_scale = self.base_scale
        self.scale_history = [self.base_scale] * 5
        
        # Camera configuration
        self.camera_config = viz_config["camera"]
    
    def _load_simulation_results(self, file_path):
        """Load simulation results from a JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _prepare_config(self):
        """Merge the loaded configuration with defaults"""
        # Start with the defaults
        merged_config = DEFAULT_VISUALIZER_CONFIG.copy()
        
        # Get user config from simulation results
        user_config = self.simulation_data.get("config", {})
        
        # Helper function to recursively merge dictionaries
        def merge_dicts(default_dict, user_dict):
            result = default_dict.copy()
            for key, value in user_dict.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        # Merge user config with defaults
        return merge_dicts(merged_config, user_config)
    
    def _setup_colors(self):
        """Setup colors from config"""
        viz_config = self.config["visualization"]
        colors = viz_config["colors"]
        
        return {
            "background": colors["background"],
            "positive": colors["positive"],
            "negative": colors["negative"],
            "tracer": colors["tracer"],
            "tracer_positive": colors.get("tracer_positive", "#FC6255"),  # Default to PALE RED if not specified
            "tracer_negative": colors.get("tracer_negative", "#58C4DD")   # Default to PALE BLUE if not specified
        }
    
    def _get_particle_color(self, charge):
        """Get the color for a particle based on its charge"""
        return self.colors["positive"] if charge > 0 else self.colors["negative"]
        
    def _get_tracer_color(self, charge):
        """Get the color for a particle's tracer based on its charge and settings"""
        if self.tracer_config.get("use_particle_color", True):
            return self.colors["tracer_positive"] if charge > 0 else self.colors["tracer_negative"]
        else:
            return self.colors["tracer"]
    
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
        # Set up the scene with camera configuration from config
        phi = self.camera_config["phi"] * DEGREES
        theta = self.camera_config["theta"] * DEGREES
        self.set_camera_orientation(phi=phi, theta=theta)
        self.camera.background_color = self.colors["background"]
        
        # Add axes for reference
        axes = ThreeDAxes(
            axis_config={
                "stroke_width": 1,  # Controls thickness of all axes
            },
            x_range=[-5, 5, 1],  # min, max, step (this affects ticks)
            y_range=[-5, 5, 1],
            z_range=[-5, 5, 1],
        )
        self.add(axes)
        
        # Create scale indicator with ValueTracker for dynamic updating
        # We'll always show the scale, even if scaling is disabled
        self.scale_tracker = ValueTracker(self.base_scale)
        
        # Create a more robust scale indicator
        # Create a fixed-in-frame camera for 2D elements that should remain fixed
        self.fixed_camera = self.camera
        
        # Function to update the scale text
        def update_scale_text(text):
            text.become(Text(f"Scale: {self.scale_tracker.get_value():.2f}", font_size=24, color=WHITE).to_corner(UR, buff=0.5))
            return text
            
        # Create a single text object with both label and value
        self.scale_indicator = Text(f"Scale: {self.base_scale:.2f}", font_size=24, color=WHITE)
        self.scale_indicator.to_corner(UR, buff=0.5)
        self.scale_indicator.add_updater(update_scale_text)
        
        # Add as fixed in frame
        self.add_fixed_in_frame_mobjects(self.scale_indicator)
        
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
            if self.tracer_config["enabled"]:
                # Determine tracer color based on settings and particle charge
                tracer_color = self._get_tracer_color(charge)
                
                # Create tracer with all parameters from config
                tracer = TracingTail(
                    particle,
                    max_points=self.tracer_config["history_length"],
                    stroke_color=tracer_color,
                    stroke_width=self.tracer_config.get("stroke_width", 1),
                    add_spheres=self.tracer_config.get("add_spheres", False),
                    frames_between_spheres=self.tracer_config.get("frames_between_trail_segments", 60),
                    sphere_radius=self.tracer_config.get("sphere_radius", self.marker_size/2),
                    max_sphere_radius=self.tracer_config.get("max_sphere_radius", self.marker_size)
                )
                self.add(tracer)
                tracers[p_id_str] = tracer
            
            # Add particle AFTER tracer so it appears on top
            self.add(particle)
            particles.append((particle, positions, p_id_str, charge))
        
        # Create a group to hold history lines
        history_lines = VGroup()
        self.add(history_lines)
        
        # Dictionary to store potential wave connections
        # Format: {(emitter_id, receiver_id): [(emitter_hist_pos, receiver_hist_pos, sim_time), ...]}
        # These are fixed pairs that show exactly where the emitter was when it emitted the wave
        # and where the receiver was when the wave reached it
        potential_connections = {}
        
        # Animate the simulation
        sampling_rate = self.sim_to_manim_ratio
        
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
            
            # Clear previous history lines
            history_lines.submobjects = []
            
            # Update draw flag - we will draw history lines on EVERY frame but only 
            # recalculate new connections periodically
            draw_history_lines = self.history_lines_config["enabled"]
            
            # Flag to determine if we should recalculate connections this frame
            calculate_connections = draw_history_lines and (i % self.history_lines_config.get("update_interval", 30) == 0)
            
            for particle, positions, p_id_str, charge in particles:
                if i < len(positions):
                    pos = positions[i]
                    new_pos = [current_scale * p for p in pos]
                    
                    # Use a smoother animation with a shorter run time to reduce jumpiness
                    animations.append(particle.animate.move_to(new_pos))
                    
                    # Skip if history lines are not enabled
                    if not self.history_lines_config["enabled"]:
                        continue
                        
                    # Only calculate potential connections at specified intervals
                    # or if we don't have enough history
                    if i < 10 or not calculate_connections:
                        continue
                        
                    # For each pair of particles, find the correct historical position
                    # that would have emitted a potential wave to reach the current position
                    for other_particle, other_positions, other_id, other_charge in particles:
                        # Skip self-interaction
                        if p_id_str == other_id:
                            continue
                            
                        # Get current receiver position
                        receiver_pos = new_pos
                        
                        # Find the historical emitter position
                        # This mimics the algorithm in action_history.py
                        best_hist_idx = 0
                        best_remaining_distance = float('inf')
                        
                        # Get potential velocity from global config first, fallback to history_lines
                        global_config = self.config.get("global", {})
                        potential_velocity = global_config.get("potential_velocity", 
                                     self.history_lines_config.get("potential_velocity", 10.0))
                        
                        # Search through history points to find the best match
                        for hist_idx in range(min(i, len(other_positions))):
                            # Skip if we don't have enough history
                            if hist_idx >= len(other_positions):
                                continue
                                
                            # Get historical emitter position
                            hist_emitter_pos = other_positions[hist_idx]
                            
                            # Calculate how many time steps back this history point is
                            steps_back = i - hist_idx
                            
                            # Calculate the distance from historical position to current receiver
                            rx, ry, rz = receiver_pos[0], receiver_pos[1], receiver_pos[2]
                            ex, ey, ez = hist_emitter_pos[0], hist_emitter_pos[1], hist_emitter_pos[2]
                            hist_to_receiver_distance = math.sqrt((rx-ex)**2 + (ry-ey)**2 + (rz-ez)**2)
                            
                            # Calculate how far the potential wave would have traveled by now
                            wave_travel_distance = steps_back * (self.config["simulation"]["dt"]) * potential_velocity
                            
                            # Calculate the remaining distance between the wave front and the receiver
                            remaining_distance = abs(hist_to_receiver_distance - wave_travel_distance)
                            
                            # If this wave front is closer to the receiver than our current best,
                            # update our best match
                            if remaining_distance < best_remaining_distance:
                                best_hist_idx = hist_idx
                                best_remaining_distance = remaining_distance
                        
                        # Store connection if the potential wave is close enough
                        if best_remaining_distance < 0.1 and best_hist_idx > 0:
                            # Get the best historical emitter position
                            best_hist_pos = other_positions[best_hist_idx]
                            
                            # Create a key for this particle pair relation
                            relation_key = (other_id, p_id_str)
                            
                            # Create a new entry if it doesn't exist
                            if relation_key not in potential_connections:
                                potential_connections[relation_key] = []
                            
                            # Store the FIXED PAIR of positions with simulation time
                            # This gives us the exact points where emitter emitted and receiver received
                            connection = (best_hist_pos, pos, i)  # Use current pos as fixed receiver position
                            potential_connections[relation_key].append(connection)
                            
                            # Print debug to confirm connections are being stored
                            print(f"Stored connection: emitter {other_id} → receiver {p_id_str}, time: {i}, remaining distance: {best_remaining_distance:.5f}")
                            
            # We've finished all per-particle calculations
            # Now draw the history lines on each frame if enabled
            if draw_history_lines:
                # Clear previous history lines
                history_lines.submobjects = []
                
                # Draw lines for each particle relation
                lines_per_relation = self.history_lines_config.get("lines_per_relation", 3)
                
                for relation_key, connections in potential_connections.items():
                    emitter_id, receiver_id = relation_key
                    
                    # Sort connections by time (newest to oldest)
                    sorted_connections = sorted(connections, key=lambda x: x[2], reverse=True)
                    
                    # Take only the most recent connections up to lines_per_relation
                    recent_connections = sorted_connections[:lines_per_relation]
                    
                    # Draw lines for these connections
                    for hist_emitter_pos, hist_receiver_pos, sim_time in recent_connections:
                        # Scale both historical positions
                        scaled_hist_emitter_pos = [current_scale * p for p in hist_emitter_pos]
                        scaled_hist_receiver_pos = [current_scale * p for p in hist_receiver_pos]
                        
                        # Determine emitter charge to set connection color
                        emitter_charge = 0
                        for particle, positions, p_id, charge in particles:
                            if p_id == emitter_id:
                                emitter_charge = charge
                                break
                                
                        # Set connection color based on emitter charge
                        if emitter_charge > 0:
                            connection_color = self.colors["tracer_positive"]  # PALE RED
                        else:
                            connection_color = self.colors["tracer_negative"]  # PALE BLUE
                            
                        # Calculate the direction vector 
                        direction = np.array(scaled_hist_receiver_pos) - np.array(scaled_hist_emitter_pos)
                        direction_norm = np.linalg.norm(direction)
                        
                        # Skip if endpoints are too close
                        if direction_norm < 0.01:
                            continue
                        
                        # Simply create a dotted line that connects directly from emitter to receiver
                        # Calculate the dash length based on the line length
                        # Shorter lines get smaller dashes for better visual density
                        dash_length = min(0.1, max(0.03, direction_norm / 20))
                        
                        # Create a dashed line with the appropriate color
                        dashed_line = DashedLine(
                            start=scaled_hist_emitter_pos,
                            end=scaled_hist_receiver_pos,  # Connect directly to receiver position
                            stroke_width=self.history_lines_config["stroke_width"],
                            stroke_color=connection_color,
                            dash_length=dash_length,
                            dashed_ratio=0.5
                        )
                        
                        # Add the line to our history lines group
                        history_lines.add(dashed_line)
            
            if animations:
                # Use even shorter run time and linear rate for smoother motion
                self.play(*animations, run_time=0.05, rate_func=linear)
                
                # Update scale indicator using the ValueTracker
                # This will automatically update the DecimalNumber through the updater
                self.scale_tracker.set_value(current_scale)
        
        # Final pause
        self.wait(2)


# Dynamic class creation for concurrent runs
custom_class_name = os.environ.get("VISUALIZATION_CLASS_NAME", "PotentialVisualization")
if custom_class_name != "PotentialVisualization":
    # Create a new class with the unique name that inherits from PotentialVisualization
    globals()[custom_class_name] = type(custom_class_name, (PotentialVisualization,), {})
    print(f"Created dynamic visualization class: {custom_class_name}")

if __name__ == "__main__":
    try:
        # When run directly, render the visualization
        print("Rendering visualization...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)