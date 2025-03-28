#\!/usr/bin/env python3
"""
Test Zoom Animation Script
"""

import os
import sys
import json
from zoom_animation import ZoomAnimation
from manim import config

def main():
    """Main entry point for the script"""
    # Set the config file to be used
    os.environ['ZOOM_CONFIG_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config.json')
    
    # Set low quality for faster rendering
    config.quality = "l"
    config.preview = True
    
    # Import and run the ZoomAnimation
    os.system("manim test_zoom.py ZoomAnimation -ql --disable_caching -p")
    
# Import the ZoomAnimation class
from zoom_animation import ZoomAnimation

if __name__ == "__main__":
    main()
