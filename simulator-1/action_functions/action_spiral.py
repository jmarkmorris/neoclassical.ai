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
    "initial_theta": 0.0,      # Starting theta value
    "potential_velocity": 10.0 # Potential wave propagation velocity (for history lines)
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
        
        # Get potential velocity for history lines from global config or physics config
        global_config = self.config.get("global", {})
        self.potential_velocity = global_config.get("potential_velocity", 
                               physics_config.get("potential_velocity", 
                                        DEFAULT_SPIRAL_PARAMS["potential_velocity"]))
        
        # Store theta values for each particle
        self.particle_thetas = {}  # Will be initialized on first apply
        
        # Direction of spiral is based solely on sign of spiral_k
        spiral_direction = "inward" if self.spiral_k < 0 else "outward"
        print(f"Spiral Action initialized with: k={self.spiral_k} ({spiral_direction} spiral), theta_rate={self.theta_rate}, z_factor={self.z_factor}")
    
    def logarithmic_spiral(self, k, theta, initial_radius, initial_theta, center_x=0, center_y=0, z_offset=0):
        """
        Calculates the x, y, z coordinates of a logarithmic spiral.
        
        Args:
            k: The growth factor of the spiral. Can be positive or negative.
            theta: The current angle parameter (increases over time).
            initial_radius: Starting radius derived from particle's initial position.
            initial_theta: Starting angle derived from particle's initial position.
            center_x: X-coordinate of the spiral center.
            center_y: Y-coordinate of the spiral center.
            z_offset: Base z-coordinate.
            
        Returns:
            A Vector3D representing the coordinates on the spiral.
        """
        # Calculate the radius (distance from the origin)
        # The key is that each particle starts at its own theta (initial_theta) on the spiral
        # and then advances from there with theta
        effective_theta = theta
        r = initial_radius * np.exp(k * effective_theta)
        
        # Convert polar coordinates (r, theta) to Cartesian coordinates (x, y)
        # Use the initial_theta + effective_theta to place particle at correct angle
        angle = initial_theta + effective_theta
        x = center_x + r * np.cos(angle)
        y = center_y + r * np.sin(angle)
        
        # Calculate z using a simple oscillating function based on theta
        z = z_offset + r * self.z_factor * np.sin(angle)
        
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
                
                print(f"Initialized particle {p.id} with initial_pos={initial_pos}, initial_theta={initial_theta:.2f} radians ({initial_theta * 180/math.pi:.0f}°)")
                
                # Store the particle's initial theta - this ensures each particle starts 
                # at a different position on its spiral path
                self.particle_thetas[p.id] = initial_theta
                
                # Calculate initial radius from particle's initial position
                initial_radius = initial_pos.norm()
                
                # Log the initial position and radius for verification
                print(f"Particle {p.id}: Initial position {initial_pos}, radius {initial_radius}")
                
                # Make sure radius is never zero
                if initial_radius < 0.01:
                    initial_radius = 1.0  # Default radius if at origin
                    print(f"  -> Using default radius 1.0 since original was too small")
                
                # Store settings specific to this particle ID
                # Each particle has its own independent spiral parameters
                self.particle_data[p.id] = {
                    # Use (0,0,0) as the spiral center for all particles
                    'spiral_center': Vector3D(0, 0, 0),
                    'spiral_k': self.spiral_k,  # Use the same spiral_k value for all particles
                    'initial_radius': initial_radius,  # Use initial position distance as radius
                    'initial_theta': initial_theta     # Store the initial angle for this particle
                }
        
        # Update each particle's position based on its current theta
        for p in particles:
            # Increment theta (advance along the spiral)
            delta_theta = math.pi / self.theta_rate
            self.particle_thetas[p.id] += delta_theta
            
            # Calculate new position on the spiral
            particle_data = self.particle_data[p.id]
            spiral_center = particle_data['spiral_center']
            
            # Reset particle_thetas to 0 for the first application of this code
            # to ensure we use the initial_theta stored in particle_data
            if not hasattr(p, '_spiral_theta_initialized'):
                self.particle_thetas[p.id] = 0.0
                p._spiral_theta_initialized = True
            
            new_position = self.logarithmic_spiral(
                particle_data['spiral_k'], 
                self.particle_thetas[p.id],  # This is how far the particle has moved along its spiral
                initial_radius=particle_data['initial_radius'],
                initial_theta=particle_data['initial_theta'],  # Starting angle for this particle
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