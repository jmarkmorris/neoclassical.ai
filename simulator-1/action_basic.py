"""
Basic action function for the NPQG simulator.
This implements the default physics used for calculating particle interactions.
"""

from typing import List, Dict, Any
import math

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
                    forces[p1.id][0] += force[0]
                    forces[p1.id][1] += force[1]
                    forces[p1.id][2] += force[2]
        
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
        # Get position vectors
        r_vec = [
            p2.position.x - p1.position.x,
            p2.position.y - p1.position.y,
            p2.position.z - p1.position.z
        ]
        
        # Calculate distance
        r_squared = r_vec[0]**2 + r_vec[1]**2 + r_vec[2]**2
        r = math.sqrt(r_squared)
        
        # Avoid division by zero and very small distances
        if r < self.min_distance:
            r = self.min_distance
            # Normalize vector and scale to min distance
            magnitude = math.sqrt(r_squared)
            if magnitude > 0:
                r_vec = [
                    r_vec[0] / magnitude * self.min_distance,
                    r_vec[1] / magnitude * self.min_distance,
                    r_vec[2] / magnitude * self.min_distance
                ]
                r_squared = self.min_distance ** 2
        
        # Calculate velocity magnitude of p2
        velocity_magnitude = math.sqrt(
            p2.velocity.x**2 + p2.velocity.y**2 + p2.velocity.z**2
        )
        
        # Avoid division by zero for velocity
        if velocity_magnitude < self.min_velocity:
            velocity_magnitude = self.min_velocity
        
        # Modified Coulomb's law to ensure opposite charges attract and like charges repel
        # Using negative of product to reverse the natural behavior
        force_magnitude = -self.coulomb_constant * p1.charge * p2.charge / (r_squared * velocity_magnitude)
        
        # Calculate force direction (unit vector)
        unit_vector = [
            r_vec[0] / r,
            r_vec[1] / r,
            r_vec[2] / r
        ]
        
        # Calculate force vector
        force = [
            force_magnitude * unit_vector[0],
            force_magnitude * unit_vector[1],
            force_magnitude * unit_vector[2]
        ]
        
        # Output debug for large forces
        if abs(force_magnitude) > self.large_force_threshold:
            print(f"Large force: {force_magnitude:.2f} on particle {p1.id} from {p2.id}")
        
        return force