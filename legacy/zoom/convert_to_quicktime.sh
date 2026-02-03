#!/bin/bash
# Script to convert Manim animation to QuickTime-compatible format

# Path to the animation file
INPUT_FILE="media/videos/zoom_animation/1080p60/ZoomAnimation.mp4"
OUTPUT_FILE="media/videos/zoom_animation/1080p60/ZoomAnimation_qt.mov"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file not found: $INPUT_FILE"
    echo "Please wait for the animation to complete before running this script."
    exit 1
fi

# Convert to QuickTime-compatible format
echo "Converting to QuickTime-compatible format..."
ffmpeg -y -i "$INPUT_FILE" -vcodec prores -profile:v 3 -q:v 5 -acodec pcm_s16le "$OUTPUT_FILE"

# Check if conversion was successful
if [ $? -eq 0 ]; then
    echo "Conversion successful!"
    echo "QuickTime-compatible file is available at: $OUTPUT_FILE"
    echo "You can open it with: open $OUTPUT_FILE"
else
    echo "Conversion failed."
    echo "Try using a different codec or format."
    
    # Try alternative format (MOV with H.264)
    echo "Trying alternative format (MOV with H.264)..."
    OUTPUT_FILE_ALT="media/videos/zoom_animation/1080p60/ZoomAnimation_qt_alt.mov"
    ffmpeg -y -i "$INPUT_FILE" -vcodec h264 -pix_fmt yuv420p -acodec aac "$OUTPUT_FILE_ALT"
    
    if [ $? -eq 0 ]; then
        echo "Alternative conversion successful!"
        echo "QuickTime-compatible file is available at: $OUTPUT_FILE_ALT"
        echo "You can open it with: open $OUTPUT_FILE_ALT"
    fi
fi