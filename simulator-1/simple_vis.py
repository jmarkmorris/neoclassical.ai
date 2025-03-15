import json
import os
import sys
import numpy as np
from manim import *

class SimplePotentialScene(ThreeDScene):
    def construct(self):
        # Load the simulation results
        with open('simulation_results.json', 'r') as f:
            data = json.load(f)
        
        # Extract particles data
        particle_data = data['particle_data']
        particles = []
        
        # Set up the scene
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.camera.background_color = "#4B0082"  # INDIGO
        
        # Create a reference coordinate system
        axes = ThreeDAxes()
        self.add(axes)
        
        # Get visualization config
        config = data.get('config', {})
        viz_config = config.get('visualization', {})
        marker_size = viz_config.get('marker_size', 0.04)
        use_dot3d = viz_config.get('use_dot3d', True)
        
        # Define manim display space limits
        max_display_limit = 5.0  # Maximum allowed coordinate in Manim space
        min_display_limit = 2.0  # Minimum coordinate range to display (prevents excessive zoom)
        
        # Create scale indicator text in the upper right corner
        # Use a smaller font and adjust the positioning to be more compact
        scale_indicator = Text("Scale: 3.0", font_size=20).to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.2)
        self.add(scale_indicator)
        
        # Create particles
        for p_id, p_data in particle_data.items():
            positions = p_data['positions']
            
            # Determine color based on charge
            particles_config = config.get('simulation', {}).get('particles', [])
            charge = 0
            
            for p_cfg in particles_config:
                if str(p_cfg.get('id')) == p_id:
                    charge = p_cfg.get('charge', 0)
                    break
            
            # Use PURE_RED and PURE_BLUE as specified
            color = PURE_RED if charge > 0 else PURE_BLUE
            
            # Create particle representation
            if use_dot3d:
                # Use Dot3D with radius from config (now 0.04)
                particle = Dot3D(radius=marker_size, color=color)
            else:
                # Fallback to Sphere if not using Dot3D
                particle = Sphere(radius=marker_size, color=color)
            
            # Initial scale and position
            base_scale = 3.0  # Starting scale factor
            initial_pos = [base_scale * p for p in positions[0]]
            particle.move_to(initial_pos)
            
            self.add(particle)
            particles.append((particle, positions))
        
        # Create a path for animation
        # Sample fewer frames to reduce processing time
        sampling_rate = 10  # Use every 10th frame to reduce total number of frames
        
        # Scale stabilization variables
        last_scale = 3.0  # Track the last used scale
        scale_stability_threshold = 0.1  # Only change scale if it differs by this much
        
        for i in range(0, len(data['times']), sampling_rate):
            if i >= len(data['times']):
                break
                
            # Determine appropriate scale for this frame
            all_positions = []
            for _, pos_data in particle_data.items():
                if i < len(pos_data['positions']):
                    all_positions.append(pos_data['positions'][i])
            
            # Calculate the maximum absolute coordinate across all dimensions and particles
            max_coord = 0
            for pos in all_positions:
                max_abs = max(abs(p) for p in pos)
                if max_abs > max_coord:
                    max_coord = max_abs
            
            # Calculate the range between the particles (for minimum scaling)
            min_pos = [float('inf'), float('inf'), float('inf')]
            max_pos = [float('-inf'), float('-inf'), float('-inf')]
            
            for pos in all_positions:
                for dim in range(3):
                    if dim < len(pos):  # Ensure index is in range
                        min_pos[dim] = min(min_pos[dim], pos[dim])
                        max_pos[dim] = max(max_pos[dim], pos[dim])
            
            # Calculate the maximum range across all dimensions
            ranges = [max_pos[dim] - min_pos[dim] for dim in range(3) if min_pos[dim] != float('inf') and max_pos[dim] != float('-inf')]
            max_range = max(ranges) if ranges else 0
            
            # Define base scale (the default scaling factor)
            base_scale = 3.0
            
            # Adaptive scaling logic with improved stability:
            if max_coord > 0:
                
                # TRIGGER #1: Scale DOWN when max coordinate is too large
                # Threshold for scaling down: when max_coord * base_scale > max_display_limit
                need_scale_down = max_coord * base_scale > max_display_limit
                
                # Calculate scale down factor (only applied when needed)
                scale_down_factor = max_display_limit / max_coord if need_scale_down else base_scale
                
                # TRIGGER #2: Scale UP when particles get too close
                # Threshold for scaling up: when max_range * base_scale < min_display_limit
                need_scale_up = max_range > 0 and max_range * base_scale < min_display_limit
                
                # Calculate scale up factor (only applied when needed)
                scale_up_factor = min_display_limit / max_range if need_scale_up else base_scale
                # Limit maximum zoom to 2x base scale
                scale_up_factor = min(scale_up_factor, base_scale * 2.0)
                
                # Calculate the suggested scale 
                suggested_scale = base_scale  # Default
                if need_scale_down:
                    suggested_scale = scale_down_factor  # Scale down takes priority
                elif need_scale_up:
                    suggested_scale = scale_up_factor
                
                # Apply scale stability - only change if difference exceeds threshold
                scale_diff = abs(suggested_scale - last_scale)
                if scale_diff > scale_stability_threshold:
                    current_scale = suggested_scale
                    last_scale = current_scale  # Update last scale
                else:
                    current_scale = last_scale  # Keep the last scale
                
                # Add debug info
                print(f"Frame {i}: max_coord={max_coord:.2f}, max_range={max_range:.2f}")
                print(f"  suggested={suggested_scale:.2f}, current={current_scale:.2f}, diff={scale_diff:.2f}")
                print(f"  need_scale_down={need_scale_down}, need_scale_up={need_scale_up}")
            else:
                current_scale = base_scale
            
            # Update scale indicator
            animations = [
                scale_indicator.animate.become(
                    Text(f"Scale: {current_scale:.2f}", font_size=20).to_corner(UR).shift(LEFT * 0.5 + DOWN * 0.2)
                )
            ]
            
            # Move particles to their new positions with the adjusted scale
            for particle, positions in particles:
                if i < len(positions):
                    pos = positions[i]
                    new_pos = [current_scale * p for p in pos]
                    animations.append(particle.animate.move_to(new_pos))
            
            if animations:
                self.play(*animations, run_time=0.1)
        
        # Final pause
        self.wait(2)