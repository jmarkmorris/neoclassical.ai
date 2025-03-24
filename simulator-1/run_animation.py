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
    """Generate a unique identifier based on timestamp, random number, and process ID"""
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

def run_visualization(results_file, config_file, quality="l", preview=True, no_fail=False):
    """Run the visualization using the simulation results"""
    # Set environment variable for the results file
    os.environ["SIMULATION_RESULTS"] = results_file
    
    # Generate a unique name for the output file based on config name and unique id
    config_name = extract_config_name(config_file)
    unique_id = generate_unique_id()
    
    # Create a unique subfolder for this run to avoid partial_movie_file_list.txt conflicts
    unique_folder = f"visualizer_{unique_id}"
    
    # Read the config file to identify the action function
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            action_function = config_data.get("simulation", {}).get("action_function", "basic")
    except:
        action_function = "unknown"
    
    # Create a descriptive output name
    output_name = f"Vis_{config_name}_{action_function}_{unique_id}"
    
    # Set environment variable for the output filename
    os.environ["VISUALIZATION_OUTPUT_NAME"] = output_name
    
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
    
    # Add preview flag if needed
    if preview:
        cmd.append("-p")
    
    # Add file and scene
    # Use custom output directory to prevent conflicts in concurrent runs
    cmd.extend([
        "--output_file", unique_folder,
        "visualizer.py", 
        "PotentialVisualization"
    ])
    output_dir = f"media/videos/{unique_folder}/{quality_folder}"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set environment variable for Manim to use a custom output directory
    os.environ["MEDIA_DIR"] = os.path.abspath("media")
    os.environ["VIDEO_DIR"] = os.path.abspath(f"media/videos/{unique_folder}")
    
    # Execute Manim command
    print(f"Executing: {' '.join(cmd)}")
    
    # Keep track of existing files before running manim
    existing_files = set()
    if os.path.exists(output_dir):
        existing_files = set(os.listdir(output_dir))
    
    # Run Manim with retry logic
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            subprocess.run(cmd, check=True)
            
            # Find new files that were created
            new_files = set()
            if os.path.exists(output_dir):
                new_files = set(os.listdir(output_dir)) - existing_files
            
            # Get the path to the latest created MP4 file
            mp4_files = [f for f in new_files if f.endswith(".mp4")]
            if mp4_files:
                latest_file = max(mp4_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
                src_path = os.path.join(output_dir, latest_file)
                
                # Create destination path with our custom name
                dest_path = os.path.join(output_dir, f"{output_name}.mp4")
                
                # Rename the file
                if src_path != dest_path and os.path.exists(src_path):
                    os.rename(src_path, dest_path)
                    print(f"Renamed output file to: {dest_path}")
                    expected_path = dest_path
                else:
                    expected_path = src_path
                    
                print(f"Visualization completed. Video saved to: {expected_path}")
                return expected_path
            else:
                print("No MP4 file was created by Manim.")
                if retry_count < max_retries - 1:
                    retry_count += 1
                    print(f"Retrying ({retry_count}/{max_retries})...")
                    # Generate a new unique ID for the retry
                    unique_id = generate_unique_id()
                    unique_folder = f"visualizer_{unique_id}"
                    cmd[cmd.index("--output_file") + 1] = unique_folder
                    output_dir = f"media/videos/{unique_folder}/{quality_folder}"
                    os.makedirs(output_dir, exist_ok=True)
                    os.environ["VIDEO_DIR"] = os.path.abspath(f"media/videos/{unique_folder}")
                    continue
                else:
                    print("Max retries reached. Could not generate video.")
                    return None
                
        except subprocess.CalledProcessError as e:
            print(f"Error during visualization: {e}")
            if "already exists" in str(e) or "Permission denied" in str(e) or "file list" in str(e):
                if retry_count < max_retries - 1:
                    retry_count += 1
                    print(f"Encountered a file conflict. Retrying ({retry_count}/{max_retries})...")
                    # Generate a new unique ID for the retry
                    unique_id = generate_unique_id()
                    unique_folder = f"visualizer_{unique_id}"
                    cmd[cmd.index("--output_file") + 1] = unique_folder
                    output_dir = f"media/videos/{unique_folder}/{quality_folder}"
                    os.makedirs(output_dir, exist_ok=True)
                    os.environ["VIDEO_DIR"] = os.path.abspath(f"media/videos/{unique_folder}")
                    time.sleep(1)  # Short delay before retry
                    continue
            raise
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
