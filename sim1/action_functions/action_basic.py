"""
Basic action function for the NPQG simulator.
This implements the default physics used for calculating particle interactions.
"""

from typing import List, Dict, Any
import math
from simulator import Vector3D

# Default physical constants
DEFAULT_PHYSICS = {
    "coulomb_constant": 0.8,   # Coulomb force constant
    "min_distance": 0.001,     # Minimum particle separation to prevent extreme forces
    "min_velocity": 0.001,     # Minimum velocity magnitude to prevent division by zero
    "large_force_threshold": 10.0  # Threshold above which to warn about large forces
}

class ActionBasic:
    """Basic implementation of action function that computes forces and updates particle positions"""
    
    def __init__(self, config=None):
        """Initialize with configuration parameters"""
        self.config = config or {}
        # Extract physics parameters from config
        physics_config = self.config.get("physics", {})
        self.coulomb_constant = physics_config.get("coulomb_constant", DEFAULT_PHYSICS["coulomb_constant"])
        self.min_distance = physics_config.get("min_distance", DEFAULT_PHYSICS["min_distance"])
        self.min_velocity = physics_config.get("min_velocity", DEFAULT_PHYSICS["min_velocity"])
        self.large_force_threshold = physics_config.get("large_force_threshold", DEFAULT_PHYSICS["large_force_threshold"])
    
    def apply(self, particles, dt):
        """
        Apply physics to update particle positions and velocities
        
        Args:
            particles: List of particle objects
            dt: Time step
            
        Returns:
            Updated particles
        """
        # Calculate forces between particles
        forces = {p.id: [0, 0, 0] for p in particles}
        
        # Calculate forces between all pairs of particles
        for i, p1 in enumerate(particles):
            for j, p2 in enumerate(particles):
                if i != j:  # Skip self-interaction
                    force = self._calculate_force(p1, p2)
                    # Convert Vector3D to list for addition
                    forces[p1.id][0] += force.x
                    forces[p1.id][1] += force.y
                    forces[p1.id][2] += force.z
        
        # Update velocities based on forces
        for p in particles:
            # F = ma -> a = F/m (assuming mass=1 for simplicity)
            p.velocity.x += forces[p.id][0] * dt
            p.velocity.y += forces[p.id][1] * dt
            p.velocity.z += forces[p.id][2] * dt
            
        # Update positions based on new velocities
        for p in particles:
            p.update_position(dt)
        
        return particles
    
    def _calculate_force(self, p1, p2):
        """Calculate force between two particles using modified Coulomb's law"""
        # Calculate distance vector using Vector3D operations
        r_vec = p2.position - p1.position
        r = r_vec.norm()
        
        # Avoid division by zero and very small distances
        if r < self.min_distance:
            r = self.min_distance
            # Normalize vector and scale to min distance
            r_vec = r_vec.normalized() * self.min_distance
        
        # Calculate velocity magnitude of p2
        velocity_magnitude = p2.velocity.norm()
        
        # Avoid division by zero for velocity
        if velocity_magnitude < self.min_velocity:
            velocity_magnitude = self.min_velocity
        
        # Modified Coulomb's law to ensure opposite charges attract and like charges repel
        # Using negative of product to reverse the natural behavior
        # This makes F = -k*q1*q2/r² so:
        # - If q1 and q2 have the same sign (++ or --), force is repulsive (negative)
        # - If q1 and q2 have opposite signs (+- or -+), force is attractive (positive)
        force_magnitude = -self.coulomb_constant * p1.charge * p2.charge / (r * r * velocity_magnitude)
        
        # Calculate force vector using the normalized direction
        force = r_vec.normalized() * force_magnitude
        
        # Output debug for large forces
        if abs(force_magnitude) > self.large_force_threshold:
            print(f"Large force: {force_magnitude:.2f} on particle {p1.id} from {p2.id}")
        
        return force