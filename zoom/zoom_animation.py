#!/usr/bin/env python3
"""
NPQG Universe Zoom Animation
Main entry point for the animation renderer
"""

import argparse
import os
import sys
import subprocess
from manim import *

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.zoom_manager import ZoomManager
from core.config_loader import ConfigLoader

CONFIG_PATH = None

class ZoomAnimation(Scene):
    """Main animation controller class"""
    
    def construct(self):
        """Construct and run the animation"""
        global CONFIG_PATH
        
        # Use the global config path or default to zoom_config.json
        config_path = CONFIG_PATH or "zoom_config.json"
        
        # Load configuration
        config_loader = ConfigLoader(config_path)
        config_data = config_loader.load()
        
        # Initialize and execute the animation
        zoom_manager = ZoomManager(config_data)
        zoom_manager.execute_animation_sequence(self)

def main():
    """Main entry point for the script"""
    global CONFIG_PATH
    
    # Parse custom arguments before passing to manim
    custom_parser = argparse.ArgumentParser(add_help=False)
    custom_parser.add_argument("--config", help="Path to the JSON configuration file")
    
    # Parse only the known args to get the config path
    custom_args, remaining_args = custom_parser.parse_known_args()
    
    # Set the global config path
    if custom_args.config:
        CONFIG_PATH = custom_args.config
        print(f"Using configuration file: {CONFIG_PATH}")
    
    # Build the manim command
    cmd = ["manim"]
    
    # Add the current script
    cmd.append(__file__)
    
    # Add the scene name
    cmd.append("ZoomAnimation")
    
    # Add all remaining arguments except --config and its value
    skip_next = False
    for arg in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if arg == "--config":
            skip_next = True
            continue
        cmd.append(arg)
    
    # Print command for debugging
    print(f"Running command: {' '.join(cmd)}")
    
    # Run manim as a subprocess
    subprocess.run(cmd)

if __name__ == "__main__":
    main()