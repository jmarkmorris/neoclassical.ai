#!/usr/bin/env python3
"""
Simple wrapper to run the simple zoom animation
"""

import subprocess
import sys

def main():
    # Determine arguments
    args = ["-pql"]  # Default: preview, low quality
    
    # Add any additional args passed to this script
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    # Construct the manim command
    cmd = ["manim"] + args + ["simple_zoom.py", "SimpleZoomScene"]
    
    # Print the command for reference
    print(f"Running: {' '.join(cmd)}")
    
    # Execute the command
    subprocess.run(cmd)

if __name__ == "__main__":
    main()