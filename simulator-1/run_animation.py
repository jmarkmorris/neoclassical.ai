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
    """Generate a simple but effective unique identifier based on timestamp, random number, and process ID"""
    timestamp = int(time.time() * 1000)  # Milliseconds for better uniqueness
    rand_num = random.randint(100000, 999999)
    pid = os.getpid()  # Add process ID for better uniqueness during concurrent runs
    
    unique_id = f"{timestamp}_{rand_num}_{pid}"
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

def run_visualization(results_file, config_file, quality="h", preview=False, no_fail=False):
    """Run the visualization using the simulation results"""
    # Set environment variable for the results file
    os.environ["SIMULATION_RESULTS"] = results_file
    
    # Check if we might be running concurrent visualizations and disable preview
    # if certain environmental indicators are present
    try:
        # Look for concurrent processes running Manim
        result = subprocess.run(["pgrep", "-f", "manim"], capture_output=True, text=True)
        procs = result.stdout.strip().split('\n')
        if len(procs) > 1 and procs[0]:  # More than one Manim process (including the one we're about to start)
            print("Detected concurrent Manim processes. Ensuring preview is disabled.")
            os.environ["DISABLE_PREVIEW"] = "1"
            preview = False
    except:
        # If error checking processes, just continue
        pass
    
    # Generate a unique name for the output file based on config name and unique id
    config_name = extract_config_name(config_file)
    unique_id = generate_unique_id()
    
    # Create a unique subfolder for this run to avoid partial_movie_file_list.txt conflicts
    unique_folder = f"visualizer_{unique_id}"
    
    # We no longer need a unique class name - the unique media directory is sufficient
    unique_class_name = "PotentialVisualization"
    
    # Read the config file to identify the action function
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            action_function = config_data.get("simulation", {}).get("action_function", "basic")
    except:
        action_function = "unknown"
    
    # Create a descriptive output name
    output_name = f"Vis_{config_name}_{action_function}_{unique_id}"
    
    # Set environment variables for the output filename and class name
    os.environ["VISUALIZATION_OUTPUT_NAME"] = output_name
    os.environ["VISUALIZATION_CLASS_NAME"] = unique_class_name
    
    print(f"Using simulation data from: {results_file}")
    print(f"Output will be saved as: {output_name}")
    print("Running visualization...")
    
    # Create a temporary directory to avoid file conflicts
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="npqg_vis_")
    print(f"Using temporary directory: {temp_dir}")
    
    # Generate a unique output directory name with the unique_id to avoid collisions
    quality_folder = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}[quality]
    
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
    
    # Only add preview flag for the final output, not intermediate files
    if preview and not os.environ.get("DISABLE_PREVIEW"):
        cmd.append("-p")
    
    # Create a unique media directory but use standard "visualizer" scene name
    media_dir_name = f"media_{unique_id}"
    
    # Add file and scene with explicitly specified media directory
    cmd.extend([
        # The key fix: specify a unique media directory
        "--media_dir", media_dir_name,
        "visualizer.py", 
        unique_class_name  # Keep the unique class name
    ])
    
    # The output path uses standard Manim structure with our custom media directory
    output_dir = f"{media_dir_name}/videos/visualizer/{quality_folder}"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set environment variables for Manim
    os.environ["MEDIA_DIR"] = os.path.abspath(media_dir_name)
    os.environ["VIDEO_DIR"] = os.path.abspath(f"{media_dir_name}/videos/visualizer")
    
    # Execute Manim command
    print(f"Executing: {' '.join(cmd)}")
    
    # Run Manim
    try:
        subprocess.run(cmd, check=True)
        
        # The output file is now predictably located in the custom media directory
        output_file = os.path.join(output_dir, "PotentialVisualization.mp4")
        
        # Check if the file exists
        if os.path.exists(output_file):
            src_path = output_file
        else:
            print("No MP4 file found. The animation may have failed.")
            return None
            
        # Rename the file to something meaningful
        output_name = f"Vis_{config_name}_{action_function}"
        dest_path = os.path.join(os.path.dirname(src_path), f"{output_name}.mp4")
        
        # Rename the file
        os.rename(src_path, dest_path)
        
        print(f"Visualization completed. Video saved to: {dest_path}")
        return dest_path
    
    except Exception as e:
        print(f"Error during visualization: {e}")
        if no_fail:
            print("Continuing due to --no-fail option...")
            return None
        raise

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
    parser.add_argument("--no-fail", action="store_true",
                      help="Continue execution even if visualization fails")
    
    args = parser.parse_args()
    
    try:
        if args.visualize_only:
            # Skip simulation, just visualize
            # Use config file for naming even if we're only visualizing
            config_file = args.config
            run_visualization(args.output, config_file, quality=args.quality, 
                             preview=not args.no_preview, no_fail=args.no_fail)
        else:
            # Run simulation
            config_file = args.config
            results_file = run_simulation(config_file, args.output)
            if not args.simulate_only:
                # Run visualization if not simulate-only
                run_visualization(results_file, config_file, quality=args.quality, 
                                 preview=not args.no_preview, no_fail=args.no_fail)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
