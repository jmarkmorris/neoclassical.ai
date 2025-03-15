#!/usr/bin/env python3
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

def run_visualization():
    """Run the visualization using the simulation results"""    
    print("Running visualization...")
    
    # Run the manim command directly
    cmd = ["manim", "-p", "simple_vis.py", "SimplePotentialScene"]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Run 30-particle NPQG simulation and visualization")
    parser.add_argument("--simulate-only", action="store_true", 
                      help="Run only the simulation without visualization")
    parser.add_argument("--visualize-only", action="store_true", 
                      help="Run only the visualization using existing results file")
    
    args = parser.parse_args()
    
    # Default config and output files
    config_file = "sim30.json"
    output_file = "simulation_results.json"
    
    try:
        if args.visualize_only:
            # Skip simulation, just visualize
            run_visualization()
        else:
            # Run simulation
            run_simulation(config_file, output_file)
            if not args.simulate_only:
                # Run visualization if not simulate-only
                run_visualization()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()