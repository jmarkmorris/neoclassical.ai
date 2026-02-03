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
    """Generate a unique identifier with timestamp in human-readable format"""
    # Get current date and time in YYYYMMDD_HHMMSS format
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # Add a random number for uniqueness
    rand_num = random.randint(100000, 999999)
    
    unique_id = f"{timestamp}_{rand_num}"
    return unique_id

def extract_config_name(config_file):
    """Extract the base name from the config file without extension"""
    return os.path.splitext(os.path.basename(config_file))[0]

def run_simulation(config_file, output_file, unique_id=None):
    """Run the simulation using the specified config file"""
    # Make sure simulation_results directory exists
    os.makedirs("simulation_results", exist_ok=True)
    
    # If a unique ID was provided, create a unique output filename in the simulation_results directory
    if unique_id:
        config_name = extract_config_name(config_file)
        output_file = os.path.join("simulation_results", f"sim_{config_name}_{unique_id}.json")
    elif output_file == "simulation_results.json":
        # If no unique ID but using default output, still place in the simulation_results directory
        output_file = os.path.join("simulation_results", output_file)
    elif not os.path.dirname(output_file):
        # If output file has no directory component, place it in simulation_results
        output_file = os.path.join("simulation_results", output_file)
    
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
    
    # Generate a unique ID for this run
    unique_id = generate_unique_id()
    
    # Extract the config name
    config_name = extract_config_name(config_file)
    
    # Use a dynamic class name based on the config and action to avoid popup issues
    action_function = "unknown"
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            action_function = config_data.get("simulation", {}).get("action_function", "basic")
    except:
        pass
    unique_class_name = f"Vis_{config_name}_{action_function}"
    
    # We've already read the action function above
    
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
    
    # Don't add preview flag when we're renaming files - it causes errors
    # We'll manually open the file afterward if preview is requested
    preview_after = preview and not os.environ.get("DISABLE_PREVIEW")
    
    # Disable caching to avoid warnings and potentially speed up rendering
    cmd.append("--disable_caching")
    
    # Create parent media directory if it doesn't exist
    parent_media_dir = "media"
    os.makedirs(parent_media_dir, exist_ok=True)
    
    # Create a unique media subdirectory with the config name
    media_subdir_name = f"{config_name}_{unique_id}"
    media_dir_path = os.path.join(parent_media_dir, media_subdir_name)
    
    # Add file and scene with explicitly specified media directory
    cmd.extend([
        # Specify the media directory under the parent media directory
        "--media_dir", media_dir_path,
        "visualizer.py", 
        unique_class_name  # Keep the unique class name
    ])
    
    # The output path uses standard Manim structure with our custom media directory
    output_dir = os.path.join(media_dir_path, "videos", "visualizer", quality_folder)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set environment variables for Manim
    os.environ["MEDIA_DIR"] = os.path.abspath(media_dir_path)
    os.environ["VIDEO_DIR"] = os.path.abspath(os.path.join(media_dir_path, "videos", "visualizer"))
    
    # Execute Manim command
    print(f"Executing: {' '.join(cmd)}")
    
    # Run Manim
    try:
        subprocess.run(cmd, check=True)
        
        # The output file should be located in the custom media directory
        # Manim creates the output with the class name, not the output name
        output_file = os.path.join(output_dir, f"{unique_class_name}.mp4")
        
        # Check if the file exists
        if os.path.exists(output_file):
            src_path = output_file
            
            # Rename the file to something meaningful
            output_name = f"Vis_{config_name}_{action_function}"
            dest_path = os.path.join(os.path.dirname(src_path), f"{output_name}.mp4")
            
            # Rename the file
            os.rename(src_path, dest_path)
            
            print(f"File renamed from {src_path} to {dest_path}")
        else:
            print(f"No MP4 file found at {output_file}. Looking for other mp4 files...")
            # Try to find any mp4 files in the output directory
            mp4_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.mp4') and 'partial' not in root:
                        mp4_files.append(os.path.join(root, file))
                        
            if mp4_files:
                print(f"Found these mp4 files: {mp4_files}")
                src_path = mp4_files[0]  # Take the first one
                
                # Rename the file to something meaningful
                output_name = f"Vis_{config_name}_{action_function}"
                dest_path = os.path.join(os.path.dirname(src_path), f"{output_name}.mp4")
                
                # Rename the file
                os.rename(src_path, dest_path)
                print(f"File renamed from {src_path} to {dest_path}")
            else:
                print("No MP4 file found. The animation may have failed.")
                return None
        
        print(f"Visualization completed. Video saved to: {dest_path}")
        
        # If preview was requested, open the file
        if preview_after and os.path.exists(dest_path):
            print(f"Opening preview for {dest_path}")
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", dest_path])
                elif sys.platform == "win32":  # Windows
                    os.startfile(dest_path)
                else:  # Linux and other OS
                    subprocess.run(["xdg-open", dest_path])
            except Exception as e:
                print(f"Error opening preview: {e}")
        
        return dest_path
    
    except Exception as e:
        print(f"Error during visualization: {e}")
        if no_fail:
            print("Continuing due to --no-fail option...")
            return None
        raise

def main():
    # Ensure the simulation_results directory exists
    os.makedirs("simulation_results", exist_ok=True)
    
    parser = argparse.ArgumentParser(description="Run NPQG simulation with visualization")
    parser.add_argument("--config", "-c", default="sim_config/sim30.json", 
                      help="Path to the simulation configuration JSON file (default: sim_config/sim30.json)")
    parser.add_argument("--output", "-o", default="simulation_results.json", 
                      help="Path to save simulation results (default: simulation_results/simulation_results.json)")
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
        # Generate a single unique ID to use for both simulation and visualization
        unique_id = generate_unique_id()
        
        # Helper function to find config file
        def find_config_file(config_path):
            if os.path.exists(config_path):
                return config_path
            
            # If the path doesn't exist and doesn't have a directory component,
            # check if it's in the sim_config directory
            if not os.path.dirname(config_path):
                sim_config_path = os.path.join("sim_config", config_path)
                if os.path.exists(sim_config_path):
                    print(f"Found config file in sim_config directory: {sim_config_path}")
                    return sim_config_path
            
            # Return the original path even if not found, to allow appropriate error messages
            return config_path
        
        # Process the config path to find the actual file
        config_file = find_config_file(args.config)
            
        if args.visualize_only:
            # Skip simulation, just visualize
            # Use config file for naming even if we're only visualizing
            
            # Check if the file exists, and if not, check in the simulation_results directory
            results_file = args.output
            if not os.path.exists(results_file) and not os.path.dirname(results_file):
                simulation_results_path = os.path.join("simulation_results", results_file)
                if os.path.exists(simulation_results_path):
                    results_file = simulation_results_path
                    print(f"Using results file from simulation_results directory: {results_file}")
            
            run_visualization(results_file, config_file, quality=args.quality, 
                             preview=not args.no_preview, no_fail=args.no_fail)
        else:
            # Run simulation with the unique ID
            results_file = run_simulation(config_file, args.output, unique_id=unique_id)
            
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
