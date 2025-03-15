import os
import sys
import subprocess
import argparse

def run_simulation(config_file, output_file):
    """Run the simulation using the specified config file"""
    cmd = ["python", "simulator.py", config_file, output_file]
    print(f"Running simulation: {' '.join(cmd)}")
    
    # Run without capturing output to see progress in real-time
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Error running simulation.")
        sys.exit(1)
    
    print(f"Simulation completed. Results saved to: {output_file}")
    # Verify the output file exists
    if not os.path.exists(output_file):
        print(f"Error: Output file {output_file} not found")
        sys.exit(1)
        
    return output_file

def run_visualization(results_file):
    """Run the visualization using the simulation results"""
    cmd = ["python", "-m", "manim", "visualizer.py", "ParticleAnimation", "-p"]
    
    # Set environment variable for the results file
    env = os.environ.copy()
    env["SIMULATION_RESULTS"] = results_file
    
    print(f"Running visualization: {' '.join(cmd)}")
    print(f"Using simulation data from: {results_file}")
    
    # Run the process without capturing output to see progress in real-time
    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print(f"Error running visualization. Check if Manim is properly installed.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run NPQG simulation and visualization")
    parser.add_argument("config_file", help="Path to the simulation configuration JSON file")
    parser.add_argument("--output", "-o", default="simulation_results.json", 
                        help="Path to save simulation results (default: simulation_results.json)")
    parser.add_argument("--simulate-only", action="store_true", 
                        help="Run only the simulation without visualization")
    parser.add_argument("--visualize-only", action="store_true", 
                        help="Run only the visualization using existing results file")
    
    args = parser.parse_args()
    
    if args.visualize_only:
        run_visualization(args.config_file)  # In this case, config_file is the results file
    else:
        results_file = run_simulation(args.config_file, args.output)
        if not args.simulate_only:
            run_visualization(results_file)

if __name__ == "__main__":
    main()