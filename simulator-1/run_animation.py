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

def run_visualization(results_file, quality="l", preview=True):
    """Run the visualization using the simulation results"""
    # Set environment variable for the results file
    os.environ["SIMULATION_RESULTS"] = results_file
    
    print(f"Using simulation data from: {results_file}")
    print("Running visualization...")
    
    # Build manim command with appropriate flags
    cmd = ["manim"]
    
    # Add quality flag
    if quality == "l":
        cmd.append("-ql")  # Low quality
    elif quality == "m":
        cmd.append("-qm")  # Medium quality
    elif quality == "h":
        cmd.append("-qh")  # High quality
    elif quality == "k":
        cmd.append("-qk")  # 4K quality
    
    # Add preview flag if needed
    if preview:
        cmd.append("-p")
        
    # Add file and scene
    cmd.extend(["visualizer.py", "PotentialVisualization"])
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Run NPQG simulation with visualization")
    parser.add_argument("--config", "-c", default="sim30.json", 
                      help="Path to the simulation configuration JSON file (default: sim30.json)")
    parser.add_argument("--output", "-o", default="simulation_results.json", 
                      help="Path to save simulation results (default: simulation_results.json)")
    parser.add_argument("--simulate-only", action="store_true", 
                      help="Run only the simulation without visualization")
    parser.add_argument("--visualize-only", action="store_true", 
                      help="Run only the visualization using existing results file")
    parser.add_argument("--quality", "-q", choices=["l", "m", "h", "k"], default="h",
                      help="Visualization quality: l=low, m=medium, h=high, k=4K (default: h)")
    parser.add_argument("--no-preview", action="store_true",
                      help="Don't open the preview window after rendering")
    
    args = parser.parse_args()
    
    try:
        if args.visualize_only:
            # Skip simulation, just visualize
            run_visualization(args.output, quality=args.quality, preview=not args.no_preview)
        else:
            # Run simulation
            results_file = run_simulation(args.config, args.output)
            if not args.simulate_only:
                # Run visualization if not simulate-only
                run_visualization(results_file, quality=args.quality, preview=not args.no_preview)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
