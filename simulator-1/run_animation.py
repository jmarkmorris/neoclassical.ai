#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import random
import time
import hashlib
import re
import json
from pathlib import Path

def generate_unique_id():
    """Generate a unique identifier based on timestamp and random number"""
    timestamp = int(time.time())
    rand_num = random.randint(1000, 9999)
    unique_id = f"{timestamp}_{rand_num}"
    return unique_id

def extract_config_name(config_file):
    """Extract the base name from the config file without extension"""
    return os.path.splitext(os.path.basename(config_file))[0]

def run_simulation(config_file, output_file):
    """Run the simulation using the specified config file"""
    cmd = ["python", "simulator.py", config_file, output_file]
    print(f"Running simulation: {' '.join(cmd)}")
    
    # Run the command
    subprocess.run(cmd, check=True)
    
    print(f"Simulation completed. Results saved to: {output_file}")
    return output_file

def run_visualization(results_file, config_file, quality="l", preview=True):
    """Run the visualization using the simulation results"""
    # Set environment variable for the results file
    os.environ["SIMULATION_RESULTS"] = results_file
    
    # Generate a unique name for the output file based on config name and unique id
    config_name = extract_config_name(config_file)
    unique_id = generate_unique_id()
    
    # Read the config file to identify the action function
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            action_function = config_data.get("simulation", {}).get("action_function", "basic")
    except:
        action_function = "unknown"
    
    # Create a descriptive output name
    output_name = f"Visualization_{config_name}_{action_function}_{unique_id}"
    
    # Set environment variable for the output filename
    os.environ["VISUALIZATION_OUTPUT_NAME"] = output_name
    
    print(f"Using simulation data from: {results_file}")
    print(f"Output will be saved as: {output_name}")
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
    
    # Add output name flag (-o/--output_file is the correct manim flag)
    cmd.extend(["-o", output_name])
        
    # Add file and scene
    cmd.extend(["visualizer.py", "PotentialVisualization"])
    
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # Return the expected output path for reference
    quality_folder = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}[quality]
    expected_path = f"media/videos/visualizer/{quality_folder}/{output_name}.mp4"
    
    print(f"Visualization completed. Video saved to: {expected_path}")
    return expected_path

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
            # Use config file for naming even if we're only visualizing
            config_file = args.config
            run_visualization(args.output, config_file, quality=args.quality, preview=not args.no_preview)
        else:
            # Run simulation
            config_file = args.config
            results_file = run_simulation(config_file, args.output)
            if not args.simulate_only:
                # Run visualization if not simulate-only
                run_visualization(results_file, config_file, quality=args.quality, preview=not args.no_preview)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
