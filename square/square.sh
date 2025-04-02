#!/bin/bash

# Function to display the menu and get user choice
get_menu_choice() {
  PS3="$1"
  shift
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
SQUARE_SIZE=0.1
COLOR_SCHEME="random_color"
BORDERS="no"

# Menu for square size
square_size_options=("0.05" "0.10" "0.25" "0.5" "1.0" "2.0" "Custom")
chosen_size=$(get_menu_choice "Choose square size: " "${square_size_options[@]}")

if [[ "$chosen_size" == "Custom" ]]; then
  read -p "Enter custom square size: " SQUARE_SIZE
else
  SQUARE_SIZE="$chosen_size"
fi

echo ""

# Menu for color scheme
color_scheme_options=("alternating_red_blue" "black_and_white" "random_color" "random_red_blue")
COLOR_SCHEME=$(get_menu_choice "Choose color scheme: " "${color_scheme_options[@]}")

echo ""

# Ask about borders using a yes/no question
read -r -p "Show borders? [y/N] " BORDERS
if [[ "$BORDERS" =~ ^[yY] ]]; then
  BORDERS="yes"
else
  BORDERS="no"
fi

echo ""

# Ask about opacity using a yes/no question
read -r -p "Set opacity? [y/N] " OPACITY
if [[ "$OPACITY" =~ ^[yY] ]]; then
  OPACITY="1.0"
else
  OPACITY="0.5"
fi

# Update square.json with the chosen values
jq ".square_size = $(echo "$SQUARE_SIZE" | bc)" square.json > tmp.json && mv tmp.json square.json
jq ".color_scheme = \"$COLOR_SCHEME\"" square.json > tmp.json && mv tmp.json square.json
jq ".borders = \"$BORDERS\"" square.json > tmp.json && mv tmp.json square.json
jq ".opacity = $(echo "$OPACITY" | bc)" square.json > tmp.json && mv tmp.json square.json

# Run manim with the updated configuration
manim -pqh square.py TiledSquares
