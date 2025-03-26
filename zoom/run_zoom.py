#!/usr/bin/env python3
"""
Simple wrapper script to run the NPQG Universe Zoom Animation
This makes it easier to run the animation with common options
"""

import os
import sys
import subprocess
import argparse
import shutil

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
                       
    parser.add_argument("--opengl", action="store_true",
                       help="Use OpenGL renderer instead of Cairo (may be more stable)")
                       
    parser.add_argument("--clean", action="store_true",
                       help="Clean media directory before rendering (helps with rendering errors)")
    
    args, unknown_args = parser.parse_known_args()
    
    # Prepare manim options
    manim_args = []
    
    # Quality setting
    manim_args.extend(["-q", args.quality])
    
    # Disable caching for better performance with complex scenes
    manim_args.append("--disable_caching")
    
    # Use OpenGL renderer if specified
    if args.opengl:
        manim_args.append("-r")  # OpenGL renderer
    
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
    
    # Clean media directory if requested
    if args.clean:
        media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
        if os.path.exists(media_dir):
            print("Cleaning media directory...")
            try:
                shutil.rmtree(media_dir)
                print("Media directory cleaned successfully")
            except Exception as e:
                print(f"Error cleaning media directory: {e}")
    
    # Ensure output directories exist
    # For full mode
    if args.mode == "full":
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "media", "videos", "zoom_animation", "1080p60", 
                                "partial_movie_files", "ZoomAnimation")
    # For simple mode
    else:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "media", "videos", "simple_zoom", "1080p60", 
                                "partial_movie_files", "SimpleZoomScene")
    os.makedirs(output_dir, exist_ok=True)
    file_list = os.path.join(output_dir, "partial_movie_file_list.txt")
    if not os.path.exists(file_list):
        open(file_list, 'a').close()  # Create empty file if it doesn't exist
        
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
