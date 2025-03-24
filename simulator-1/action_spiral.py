"""
Spiral action function for the NPQG simulator.

This action function uses a logarithmic spiral to determine particle positions.
Instead of using a physics-based model like Coulomb's law, this is purely geometric.
Particles follow a logarithmic spiral path, with positions updated directly without 
using or updating velocity.
"""

import numpy as np
import math
from simulator import Vector3D

# Default parameters for the spiral action
DEFAULT_SPIRAL_PARAMS = {
    "spiral_k": 0.1,           # Spiral growth factor
    "theta_rate": 200,         # Controls how fast we advance along the spiral (smaller = faster)
    "z_factor": 0.05,          # Controls how fast z-coordinate changes
    "initial_theta": 0.0       # Starting theta value
}

class ActionSpiral:
    """
    Implementation of a geometric action function that moves particles along logarithmic spirals.
    Positions are updated directly without using or updating velocity.
    All particles follow the same spiral direction determined by the spiral_k parameter:
    - spiral_k > 0: All particles spiral outward
    - spiral_k < 0: All particles spiral inward
    The spiral direction is now independent of particle charge.
    """
    
    def __init__(self, config=None):
        """Initialize with configuration parameters"""
        self.config = config or {}
        
        # Extract spiral parameters from config
        physics_config = self.config.get("physics", {})
        self.spiral_k = physics_config.get("spiral_k", DEFAULT_SPIRAL_PARAMS["spiral_k"])
        self.theta_rate = physics_config.get("theta_rate", DEFAULT_SPIRAL_PARAMS["theta_rate"])
        self.z_factor = physics_config.get("z_factor", DEFAULT_SPIRAL_PARAMS["z_factor"])
        
        # Store theta values for each particle
        self.particle_thetas = {}  # Will be initialized on first apply
        
        # Direction of spiral is based solely on sign of spiral_k
        spiral_direction = "inward" if self.spiral_k < 0 else "outward"
        print(f"Spiral Action initialized with: k={self.spiral_k} ({spiral_direction} spiral), theta_rate={self.theta_rate}, z_factor={self.z_factor}")
    
    def logarithmic_spiral(self, k, theta, center_x=0, center_y=0, z_offset=0):
        """
        Calculates the x, y, z coordinates of a logarithmic spiral.
        
        Args:
            k: The growth factor of the spiral. Can be positive or negative.
            theta: The angle in radians. Can be any non-negative value.
            center_x: X-coordinate of the spiral center
            center_y: Y-coordinate of the spiral center
            z_offset: Base z-coordinate
            
        Returns:
            A Vector3D representing the coordinates on the spiral.
        """
        # Starting radius at theta = 0
        a = 1.0
        
        # Calculate the radius (distance from the origin)
        r = a * np.exp(k * theta)
        
        # Convert polar coordinates (r, theta) to Cartesian coordinates (x, y)
        x = center_x + r * np.cos(theta)
        y = center_y + r * np.sin(theta)
        
        # Calculate z using a simple oscillating function based on theta
        z = z_offset + r * self.z_factor * np.sin(theta)
        
        return Vector3D(x, y, z)
    
    def apply(self, particles, dt):
        """
        Apply spiral geometry to update particle positions directly without using velocity.
        
        Args:
            particles: List of particle objects
            dt: Time step
            
        Returns:
            Updated particles
        """
        # Initialize particle-specific data
        # We need to store settings for each particle instead of attaching them to the particle object
        # because the simulator may create new particle objects each time
        if not hasattr(self, 'particle_data'):
            self.particle_data = {}
            
        # Initialize settings for new particles
        for p in particles:
            if p.id not in self.particle_thetas:
                # Initialize with a value based on particle position
                initial_pos = p.position
                
                # If the particle starts at origin, give it a default initial theta
                if initial_pos.norm() < 0.01:
                    initial_theta = 0.0
                else:
                    # Calculate initial theta based on position (atan2 gives angle in [-π, π])
                    initial_theta = math.atan2(initial_pos.y, initial_pos.x)
                    if initial_theta < 0:
                        initial_theta += 2 * math.pi  # Convert to [0, 2π]
                
                self.particle_thetas[p.id] = initial_theta
                
                # Store settings specific to this particle ID
                # Use the same spiral_k value for all particles regardless of charge
                self.particle_data[p.id] = {
                    'spiral_center': Vector3D(0, 0, 0),
                    'spiral_k': self.spiral_k  # Use the same spiral_k value for all particles
                }
        
        # Update each particle's position based on its current theta
        for p in particles:
            # Increment theta (advance along the spiral)
            delta_theta = math.pi / self.theta_rate
            self.particle_thetas[p.id] += delta_theta
            
            # Calculate new position on the spiral
            particle_data = self.particle_data[p.id]
            spiral_center = particle_data['spiral_center']
            new_position = self.logarithmic_spiral(
                particle_data['spiral_k'], 
                self.particle_thetas[p.id],
                center_x=spiral_center.x,
                center_y=spiral_center.y,
                z_offset=spiral_center.z
            )
            
            # Directly update position
            p.position = new_position
            
            # Store original velocity for history
            original_velocity = p.velocity.copy()
            
            # Calculate approximate velocity based on position change
            # This is just for visualization purposes since we're not actually using velocity
            # for the physics calculations in this action function
            if dt > 0:
                # Find the previous position (may be approximate)
                if len(p.path_history) > 1:
                    prev_position = p.path_history[-1]
                    # Calculate velocity as (new_position - prev_position) / dt
                    # Calculate each component separately to avoid Vector3D math issues
                    pos_diff = new_position - prev_position
                    p.velocity.x = pos_diff.x / dt
                    p.velocity.y = pos_diff.y / dt
                    p.velocity.z = pos_diff.z / dt
                # If we don't have history yet, keep the original velocity
            
            # Store position and velocity in history directly instead of using update_position
            p.path_history.append(p.position.copy())
            p.velocity_history.append(p.velocity.copy())
            
            # Keep history within limits
            if len(p.path_history) > p.max_history:
                p.path_history.pop(0)
                p.velocity_history.pop(0)
            
            # Restore original velocity in history if we didn't want to update it
            # p.velocity_history[-1] = original_velocity
        
        return particles