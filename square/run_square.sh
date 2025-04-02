#!/bin/bash

# Smallest possible square size in manim (theoretically, but limited by computational precision)
# Largest square size that will fit: frame_width

# Function to display the menu and get user choice
get_menu_choice() {
  PS3="$1"
  select choice in "$@"; do
    if [[ -n "$choice" ]]; then
      echo "$choice"
      break
    else
      echo "Invalid choice. Please select again."
    fi
  done
}

# Set default values
SQUARE_SIZE=0.5
COLOR_SCHEME="random_color"
BORDERS="yes"

# Menu for square size
square_size_options=("0.05" "0.10" "0.25" "0.5" "1.0" "2.0" "Custom")
chosen_size=$(get_menu_choice "Choose square size:" "${square_size_options[@]}")

if [[ "$chosen_size" == "Custom" ]]; then
  read -p "Enter custom square size: " SQUARE_SIZE
else
  SQUARE_SIZE="$chosen_size"
fi

# Menu for color scheme
color_scheme_options=("alternating_red_blue" "black_and_white" "random_color")
COLOR_SCHEME=$(get_menu_choice "Choose color scheme:" "${color_scheme_options[@]}")

# Menu for borders
border_options=("yes" "no")
BORDERS=$(get_menu_choice "Show borders?" "${border_options[@]}")

# Update square.json with the chosen values
jq ".square_size = $(echo "$SQUARE_SIZE" | bc)" square.json > tmp.json && mv tmp.json square.json
jq ".color_scheme = \"$COLOR_SCHEME\"" square.json > tmp.json && mv tmp.json square.json
jq ".borders = \"$BORDERS\"" square.json > tmp.json && mv tmp.json square.json

# Run manim with the updated configuration
manim -pqh square.py TiledSquares
