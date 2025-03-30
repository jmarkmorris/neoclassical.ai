#!/usr/bin/env python3
"""
Launcher script for the zoom.py animation
Runs with the same approach as the demo
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    quality = 'l'  # Default to low quality for fast renders

    # Check if quality argument is provided
    if len(sys.argv) > 1:
        if sys.argv[1] in ['l', 'm', 'h']:
            quality = sys.argv[1]

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    zoom_script_name = "zoom.py"
    zoom_class_name = "ZoomAnimation"

    # Construct the manim command arguments
    zoom_script_path = os.path.join(script_dir, zoom_script_name)
    manim_args = [
        "manim",
	"--flush_cache",
        f"-pq{quality}",
        zoom_script_path,
        zoom_class_name
    ]

    print(f"Running command: {' '.join(manim_args)}")

    try:
        # Run the command using subprocess for better control
        process = subprocess.run(manim_args, check=False, text=True)  # check=False to see Manim's output even on error

        if process.returncode != 0:
            print(f"Manim command failed with return code {process.returncode}")
        else:
            print("Manim command executed successfully.")

    except FileNotFoundError:
        print(f"Error: 'manim' command not found. Make sure Manim is installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")
