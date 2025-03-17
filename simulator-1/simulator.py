import json
import sys
import os
import math
from typing import List, Dict, Tuple, Any, Union

# Vector operations for 3D points
class Vector3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, (list, tuple)) and len(x) >= 3:
            self.x, self.y, self.z = x[0], x[1], x[2]
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
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Division by zero")
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def dot(self, other):
        if isinstance(other, Vector3D):
            return self.x * other.x + self.y * other.y + self.z * other.z
        elif isinstance(other, (list, tuple)) and len(other) >= 3:
            return self.x * other[0] + self.y * other[1] + self.z * other[2]
        return NotImplemented
    
    def norm(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalized(self):
        magnitude = self.norm()
        if magnitude < 1e-10:
            return Vector3D(0, 0, 0)
        return self / magnitude
    
    def copy(self):
        return Vector3D(self.x, self.y, self.z)
    
    def tolist(self):
        return [self.x, self.y, self.z]
    
    def __repr__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"

class Particle:
    def __init__(self, id: int, charge: float, position: Union[Vector3D, List, Tuple], 
                 velocity: Union[Vector3D, List, Tuple]):
        self.id = id
        self.charge = charge
        
        # Convert position and velocity to Vector3D if they're not already
        self.position = position if isinstance(position, Vector3D) else Vector3D(position)
        self.velocity = velocity if isinstance(velocity, Vector3D) else Vector3D(velocity)
        
        self.path_history = [self.position.copy()]
        self.velocity_history = [self.velocity.copy()]
    
    def update_position(self, dt: float):
        """Update position based on current velocity"""
        # Calculate new position
        self.position = self.position + (self.velocity * dt)
        
        # Store history
        self.path_history.append(self.position.copy())
        self.velocity_history.append(self.velocity.copy()) 
        
        # Keep history within limits (this will be controlled by config later)
        max_history = 10000  # This would come from config
        if len(self.path_history) > max_history:
            self.path_history.pop(0)
            self.velocity_history.pop(0)
    
    def __repr__(self):
        return f"Particle(id={self.id}, charge={self.charge}, position={self.position}, velocity={self.velocity})"


class Physics:
    @staticmethod
    def coulomb_force_on_p1(particle1: Particle, particle2: Particle) -> Vector3D:
        """Calculate Coulomb force on particle1 from particle2"""
       
        k = 0.8  
        r_vec = particle2.position - particle1.position
        r = r_vec.norm()
        
        # Avoid division by zero and very small distances
        if r < 0.001:
            # Set a minimum distance to prevent extreme forces
            r = 0.001
            r_vec = r_vec.normalized() * r
        
        # Modified Coulomb's law to ensure opposite charges attract and like charges repel
        # Using negative of product to reverse the natural behavior
        # This makes F = -k*q1*q2/r² so:
        # - If q1 and q2 have the same sign (++ or --), force is repulsive (negative)
        # - If q1 and q2 have opposite signs (+- or -+), force is attractive (positive)
        force_magnitude = -k * particle1.charge * particle2.charge / (r * r * particle2.velocity.norm())
        force_direction = r_vec / r
        
        # Add debug output for large forces
        if abs(force_magnitude) > 10:
            print(f"Large force: {force_magnitude:.2f} on particle {particle1.id} from {particle2.id}")
        
        return force_magnitude * force_direction


class Simulator:
    def __init__(self, config_file: str):
        self.config = self._load_config(config_file)
        self.particles = self._initialize_particles()
        self.time = 0
        self.dt = self.config["simulation"]["dt"]
        self.duration = self.config["simulation"]["duration"]
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load simulation configuration from JSON file"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def _initialize_particles(self) -> List[Particle]:
        """Initialize particles from config"""
        particles = []
        for p_data in self.config["simulation"]["particles"]:
            particle = Particle(
                id=p_data["id"],
                charge=p_data["charge"],
                position=p_data["position"],
                velocity=p_data["velocity"]
            )
            particles.append(particle)
        return particles
    
    def run(self) -> Dict[str, List]:
        """Run the simulation and return results"""
        results = {
            "times": [],
            "particle_data": {p.id: {"positions": [], "velocities": []} for p in self.particles}
        }
        
        total_steps = int(self.duration / self.dt)
        print(f"Running simulation for {total_steps} steps...")
        
        for step in range(total_steps):
            if step % 100 == 0:
                print(f"Step {step}/{total_steps}")
                
            self._step()
            
            # Record data
            results["times"].append(self.time)
            for p in self.particles:
                results["particle_data"][p.id]["positions"].append(p.position.copy())
                results["particle_data"][p.id]["velocities"].append(p.velocity.copy())
            
            self.time += self.dt
        
        return results
    
    def _step(self):
        """Perform one simulation step"""
        forces = {p.id: Vector3D(0, 0, 0) for p in self.particles}
        
        # Calculate forces between all pairs of particles
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles):
                if i != j:  # Skip self-interaction
                    force = Physics.coulomb_force_on_p1(p1, p2)
                    forces[p1.id] = forces[p1.id] + force
        
        # Update velocities based on forces
        for p in self.particles:
            # F = ma -> a = F/m (assuming mass=1 for simplicity)
            acceleration = forces[p.id]
            p.velocity = p.velocity + (acceleration * self.dt)
        
        # Update positions based on new velocities
        for p in self.particles:
            p.update_position(self.dt)
    
    def get_simulation_state(self):
        """Return the current state of the simulation"""
        return {
            "time": self.time,
            "particles": [
                {
                    "id": p.id,
                    "charge": p.charge,
                    "position": p.position.tolist(),
                    "velocity": p.velocity.tolist(),
                    "path_history": [pos.tolist() for pos in p.path_history]
                }
                for p in self.particles
            ]
        }
    
    def save_results(self, results, output_file):
        """Save simulation results to a file"""
        # Convert Vector3D objects to lists for JSON serialization
        serializable_results = {
            "times": results["times"],
            "particle_data": {
                str(p_id): {
                    "positions": [pos.tolist() for pos in data["positions"]],
                    "velocities": [vel.tolist() for vel in data["velocities"]]
                }
                for p_id, data in results["particle_data"].items()
            },
            "config": self.config
        }
        
        print(f"Saving results to {output_file}...")
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simulator.py <config_file> [output_file]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "simulation_results.json"
    
    simulator = Simulator(config_file)
    results = simulator.run()
    simulator.save_results(results, output_file)
    print(f"Simulation completed and results saved to {output_file}")
