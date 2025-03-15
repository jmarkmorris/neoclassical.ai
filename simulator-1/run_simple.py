import os
import sys
import subprocess
import argparse

def run_simulation(config_file, output_file):
    """Run the simulation using the specified config file"""
    cmd = ["python", "simulator.py", config_file, output_file]
    print(f"Running simulation: {' '.join(cmd)}")
    
    # Run the command
    subprocess.run(cmd, check=True)
    
    print(f"Simulation completed. Results saved to: {output_file}")
    return output_file

def run_visualization(results_file):
    """Run the visualization using the simulation results"""
    # Set environment variable for the results file
    os.environ["SIMULATION_RESULTS"] = results_file
    
    print(f"Using simulation data from: {results_file}")
    print("Running visualization...")
    
    # Import and run the Manim scene directly
    from manim import config
    config.preview = True
    
    # Import after setting the environment variable
    from visualizer import ParticleAnimation
    scene = ParticleAnimation()
    scene.render()

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
    
    try:
        if args.visualize_only:
            # Use the config_file as the results file
            run_visualization(args.config_file)
        else:
            results_file = run_simulation(args.config_file, args.output)
            if not args.simulate_only:
                run_visualization(results_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()