#!/usr/bin/env python3
"""
Simple wrapper script to run the NPQG Universe Zoom Animation
This makes it easier to run the animation with common options
"""

import os
import sys
import subprocess
import argparse

def main():
    """Run the animation with common options"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run NPQG Universe Zoom Animation")
    
    parser.add_argument("--config", 
                       help="Path to JSON configuration file")
    
    parser.add_argument("--quality", choices=["l", "m", "h"], default="h",
                       help="Quality preset (l=low, m=medium, h=high). Default: h")
    
    parser.add_argument("--no-preview", action="store_true",
                       help="Disable preview mode (render to file)")
    
    parser.add_argument("--output", default="zoom_animation.mp4",
                       help="Output file name")
    
    parser.add_argument("--mode", choices=["full", "simple"], default="full",
                       help="Animation mode: full architecture or simple version")
    
    args, unknown_args = parser.parse_known_args()
    
    # Prepare manim options
    manim_args = []
    
    # Quality setting
    manim_args.extend(["-q", args.quality])
    
    # Disable caching for better performance with complex scenes
    manim_args.append("--disable_caching")
    
    # Preview mode
    if not args.no_preview:
        manim_args.append("-p")
    else:
        manim_args.extend(["-o", args.output])
    
    # Determine which script to run
    if args.mode == "simple":
        script = "simple_zoom.py"
        scene = "SimpleZoomScene"
        config_args = []
    else:
        script = "zoom_animation.py"
        scene = "ZoomAnimation"
        if args.config:
            config_args = ["--config", args.config]
        else:
            config_args = []
    
    # Build the command
    if args.mode == "simple":
        # For simple mode, run manim directly
        cmd = ["manim"] + manim_args + [script, scene] + unknown_args
    else:
        # For full mode, run through zoom_animation.py
        cmd = ["python", script] + config_args + manim_args + unknown_args
    
    print(f"Running in {args.mode} mode")
    print(f"Command: {' '.join(cmd)}")
    
    # Run the animation
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Error running animation: {e}")
        
        # Suggest troubleshooting steps
        print("\nTroubleshooting suggestions:")
        print("  1. Make sure Manim is properly installed: pip install manim")
        print("  2. If using config file, check it exists and is valid JSON")
        print("  3. Try running in simple mode: --mode simple")
        print("  4. Make sure all directories exist: assets/audio/narration")
        
        # If simple mode failed, suggest trying with vanilla manim
        if args.mode == "simple":
            print("\nYou can try running vanilla manim directly:")
            print("  manim -pql simple_zoom.py SimpleZoomScene")

if __name__ == "__main__":
    main()