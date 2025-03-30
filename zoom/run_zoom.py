#!/usr/bin/env python3
"""
Launcher script for the zoom.py animation
Runs with the same approach as the demo
"""

import os
import sys

if __name__ == "__main__":
    quality = 'l'  # Default to low quality for fast renders
    
    # Check if quality argument is provided
    if len(sys.argv) > 1:
        if sys.argv[1] in ['l', 'm', 'h']:
            quality = sys.argv[1]
    
    # Run the animation with manim
    cmd = f"manim -pq{quality} zoom.py ZoomAnimation"
    print(f"Running: {cmd}")
    os.system(cmd)
