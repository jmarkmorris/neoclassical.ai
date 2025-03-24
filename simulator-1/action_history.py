"""
Path History Action Function for the NPQG simulator.

This action function accounts for finite potential wave propagation time by:
1. Calculating the radial distance between receiver and emitter
2. Walking back through emitter's path history to find the point where the potential wave
   would have been emitted to reach the receiver's current position
3. Using that historical emitter position and velocity for action calculation

1. We look for the history point whose emitted wave is closest to the current receiver position.
2. Distance Calculation:
- For each historical emitter position, we calculate two distances:
    i. hist_to_receiver_distance: The direct distance from the historical emission point to the current receiver position.
    ii. wave_travel_distance: How far the potential wave would have traveled from that point by now (steps_back * dt * potential_velocity).
3. Finding the Best Match:
- We calculate the remaining_distance as the absolute difference between these two values.
- The smallest remaining_distance indicates the historical point whose potential wave front is closest to the receiver right now.
4. Initial Reference Point:
- We start with the current emitter position (dt = 0) as our reference point.
- Since a wave from the current emitter position hasn't traveled yet, the initial best remaining distance isplease  the direct distance between current
positions.
5. Better Debugging:
- Added a commented-out debug section that would show when we find very close matches (remaining_distance < 0.01).
- This can be uncommented if you want to see details about the wave matches.
"""

from typing import List, Dict, Any, Tuple
import math
from simulator import Vector3D

# Default physical constants
DEFAULT_PHYSICS = {
    "coulomb_constant": 0.8,       # Coulomb force constant
    "min_distance": 0.001,         # Minimum particle separation to prevent extreme forces
    "min_velocity": 0.001,         # Minimum velocity magnitude to prevent division by zero
    "large_force_threshold": 10.0  # Threshold above which to warn about large forces
}

# Default global constants
DEFAULT_GLOBAL = {
    "potential_velocity": 10.0     # Velocity of the spherical potential wave emitted by particles
}

class ActionHistory:
    """
    Implementation of action function that accounts for finite potential wave propagation time
    by searching through emitter's path history to find the appropriate emission position.
    """
    
    def __init__(self, config=None):
        """Initialize with configuration parameters"""
        self.config = config or {}
        
        # Extract physics parameters from config
        physics_config = self.config.get("physics", {})
        self.coulomb_constant = physics_config.get("coulomb_constant", DEFAULT_PHYSICS["coulomb_constant"])
        self.min_distance = physics_config.get("min_distance", DEFAULT_PHYSICS["min_distance"])
        self.min_velocity = physics_config.get("min_velocity", DEFAULT_PHYSICS["min_velocity"])
        self.large_force_threshold = physics_config.get("large_force_threshold", DEFAULT_PHYSICS["large_force_threshold"])
        
        # Extract potential wave velocity from global config, fallback to physics config for backward compatibility
        global_config = self.config.get("global", {})
        self.potential_velocity = global_config.get("potential_velocity", 
                                physics_config.get("potential_velocity", DEFAULT_GLOBAL["potential_velocity"]))
        
        print(f"Path History Action initialized with potential_velocity = {self.potential_velocity}")
    
    def apply(self, particles, dt):
        """
        Apply physics to update particle positions and velocities, considering finite potential wave propagation
        
        Args:
            particles: List of particle objects
            dt: Time step
            
        Returns:
            Updated particles
        """
        # Calculate forces between particles using history
        forces = {p.id: [0, 0, 0] for p in particles}
        
        # Calculate forces between all pairs of particles
        for receiver in particles:
            for emitter in particles:
                if receiver.id != emitter.id:  # Skip self-interaction
                    force = self._calculate_history_force(receiver, emitter, dt)
                    # Convert Vector3D to list for addition
                    forces[receiver.id][0] += force.x
                    forces[receiver.id][1] += force.y
                    forces[receiver.id][2] += force.z
        
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
    
    def _find_history_point(self, receiver, emitter, dt) -> Tuple[int, float]:
        """
        Find the position in the emitter's history with a potential wave front 
        that is closest to the current position of the receiver.
        
        Returns:
            Tuple of (history_index, remaining_distance_to_receiver)
        """
        history_length = len(emitter.path_history)
        
        # If history is too short, use the most recent history point
        if history_length <= 1:
            # Calculate distance between receiver and emitter's current position
            current_distance = (receiver.position - emitter.position).norm()
            return 0, current_distance
        
        # Initialize best match with current positions (dt = 0)
        best_idx = history_length - 1
        best_hist_position = emitter.position
        
        # For dt = 0, the wave hasn't traveled at all, so remaining distance
        # is just the current distance between emitter and receiver
        current_distance = (receiver.position - emitter.position).norm()
        best_remaining_distance = current_distance
        
        # Search through history points from newest to oldest
        for hist_idx in range(history_length - 2, -1, -1):
            # Get historical emitter position
            hist_position = emitter.path_history[hist_idx]
            
            # Calculate how many time steps back this history point is
            steps_back = history_length - 1 - hist_idx
            
            # Calculate the distance from historical position to current receiver
            hist_to_receiver_distance = (receiver.position - hist_position).norm()
            
            # Calculate how far the potential wave would have traveled by now
            wave_travel_distance = steps_back * dt * self.potential_velocity
            
            # Calculate the remaining distance between the wave front and the receiver
            # This is the absolute difference between how far the wave has traveled
            # and the distance from the emission point to the receiver
            remaining_distance = abs(hist_to_receiver_distance - wave_travel_distance)
            
            # If this wave front is closer to the receiver than our current best,
            # update our best match
            if remaining_distance < best_remaining_distance:
                best_idx = hist_idx
                best_remaining_distance = remaining_distance
                best_hist_position = hist_position
                
        # Return the best matching history point and the remaining distance
        return best_idx, best_remaining_distance
    
    def _calculate_history_force(self, receiver, emitter, dt):
        """
        Calculate force between two particles using historical emission position and velocity.
        The force on the receiver is based on the potential wave emitted by the transmitter
        at some point in its history, accounting for finite propagation time.
        """
        # Find the history point with wave front closest to the receiver
        hist_idx, remaining_distance = self._find_history_point(receiver, emitter, dt)
        
        # Get the historical position and velocity
        hist_position = emitter.path_history[hist_idx]
        hist_velocity = emitter.velocity_history[hist_idx]
        
        # Calculate distance vector using receiver's current position and emitter's historical position
        r_vec = receiver.position - hist_position
        r = r_vec.norm()
        
        # For debugging - show when wave is very close to receiver
        if remaining_distance < 0.01:
            steps_back = len(emitter.path_history) - 1 - hist_idx
            wave_travel_time = steps_back * dt
            #print(f"Close wave match: particle {emitter.id} -> {receiver.id}, "
            #      f"history point {hist_idx} ({wave_travel_time:.2f}s ago), "
            #      f"remaining distance: {remaining_distance:.5f}")
        
        # Avoid division by zero and very small distances
        if r < self.min_distance:
            r = self.min_distance
            r_vec = r_vec.normalized() * self.min_distance
        
        # Calculate velocity magnitude of historical emitter velocity
        velocity_magnitude = hist_velocity.norm()
        
        # Avoid division by zero for velocity
        if velocity_magnitude < self.min_velocity:
            velocity_magnitude = self.min_velocity
        
        # Modified Coulomb's law using historical emitter position and velocity
        # Opposite charges attract, like charges repel (standard Coulomb behavior)
        force_magnitude = self.coulomb_constant * receiver.charge * emitter.charge / (r * r * velocity_magnitude)
        
        # Calculate force vector using the normalized direction
        force = r_vec.normalized() * force_magnitude
        
        # Output debug for large forces
        if abs(force_magnitude) > self.large_force_threshold:
            print(f"Large force: {force_magnitude:.2f} on particle {receiver.id} from {emitter.id} (using history point {hist_idx})")
        
        return force