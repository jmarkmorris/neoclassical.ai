#!/bin/bash

# Check if we're in the project root directory (where pyproject.toml is)
if [ ! -f "pyproject.toml" ]; then
    echo "Please run this script from the project root directory (the one containing pyproject.toml)"
    echo "Example: cd /path/to/project/root && ./run_example.sh"
    exit 1
fi

# Check for jq dependency (needed for Square configuration)
if ! command -v jq &> /dev/null; then
    echo "Error: 'jq' command not found. Please install jq to configure the Square example."
    echo "Installation instructions: https://jqlang.github.io/jq/download/"
    exit 1
fi

# Print banner
print_banner() {
    clear
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║                 MANIM EXAMPLES LAUNCHER                    ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
}

# Function to display a menu and get user choice (ported from square.sh)
get_menu_choice() {
  PS3="$1" # Use the prompt passed as the first argument
  shift    # Remove the prompt from the arguments list
  select choice in "$@"; do
    if [[ -n "$choice" ]]; then
      echo "$choice" # Output the selected choice
      break         # Exit the loop once a valid choice is made
    else
      echo "Invalid choice. Please select again." >&2 # Error message to stderr
    fi
  done
}

# Function to list available Python files
list_tools() {
    echo "Available tools:"
    echo ""
    
    # Find directories within 'examples/' that contain a matching .py file
    # Exclude __pycache__ and any directories starting with '.'
    dirs=$(find examples -mindepth 1 -maxdepth 1 -type d ! -name '__pycache__' ! -name '.*' | sort)
    valid_tools=()
    
    # Calculate the number of columns based on terminal width
    term_width=$(tput cols)
    max_name_length=25
    num_cols=$((term_width / (max_name_length + 5)))
    
    # Ensure at least one column
    if [ $num_cols -lt 1 ]; then
        num_cols=1
    fi
    
    # Create a temporary file with numbered entries
    temp_file=$(mktemp)
    counter=1
    while read -r dir; do
        dir_basename=$(basename "$dir")
        script_path="$dir/$dir_basename.py"
        # Check if the corresponding Python file exists
        if [ -f "$script_path" ]; then
            class_name="$dir_basename"
            valid_tools+=("$class_name") # Store valid tool names
            
            # Format the entry with padding
            printf "%3d) %-${max_name_length}s" $counter "$class_name" >> "$temp_file"
            
            # Add newline if we've reached the end of a row
            if [ $((counter % num_cols)) -eq 0 ]; then
                echo "" >> "$temp_file"
            fi
            
            counter=$((counter + 1))
        fi
    done <<< "$dirs"

    # Add final newline if needed
    if [ $(((counter-1) % num_cols)) -ne 0 ]; then
        echo "" >> "$temp_file"
    fi
    
    # Display the formatted list
    cat "$temp_file"
    rm "$temp_file"
    
    echo ""
}

# Function to run the selected tool
run_tool() {
    local tool_name="$1" # This is just the class name (e.g., AngleClassUse)
    local script_path="examples/${tool_name}/${tool_name}.py" # Construct the path relative to project root
    echo "Running $tool_name from $script_path..."
    # Use python -m manim to ensure the correct environment is used
    echo "Command: python -m manim -pqk --disable_caching $script_path $tool_name -p"
    echo ""

    # Run the tool with high quality rendering using python -m manim
    python -m manim -pqk --disable_caching "$script_path" "$tool_name" -p

    echo ""
    echo "Finished running $tool_name."
    echo "Press Enter to continue..."
    read
}

# Function to display help
show_help() {
    echo "Manim Examples Help:"
    echo ""
    echo "This script allows you to run various Manim animations from the examples."
    echo ""
    echo "Commands:"
    echo "  [number]   - Run the animation with the corresponding number"
    echo "  h, help    - Display this help message"
    echo "  q, quit    - Exit the program"
    echo ""
    echo "Rendering Options:"
    echo "  All animations are rendered with high quality (-qk) settings"
    echo "  Preview is automatically shown after rendering"
    echo ""
    echo "Press Enter to continue..."
    read
}

# --- Configuration options for the Square example ---
square_size_options=("0.04" "0.05" "0.10" "0.2" "0.5" "Custom")
color_scheme_options=("alternating_red_blue" "black_and_white" "random_color" "random_red_blue")
# --- End Square configuration options ---

# Main script
while true; do
    print_banner
    list_tools
    echo "Enter the number of the tool to run, 'h' for help, or 'q' to quit: "
    read -p "> " choice

    case "$choice" in
        [0-9]*)
            # Adjust index for 0-based array access
            index=$((choice - 1))
            # Get the tool name from the valid_tools array
            tool_name="${valid_tools[$index]}"

            if [ -z "$tool_name" ]; then
                echo "Invalid selection."
                sleep 1
                continue # Go back to the start of the loop
            fi

            # --- Configuration specific to the Square example ---
            if [ "$tool_name" == "Square" ]; then
                echo ""
                echo "--- Configuring Square Example ---"

                # Set default values (can be overridden by user)
                SQUARE_SIZE=0.1
                COLOR_SCHEME="random_color"
                BORDERS="no"
                OPACITY_VARIATION="yes" # Default is variation enabled

                # Menu for square size
                chosen_size=$(get_menu_choice "Choose square size: " "${square_size_options[@]}")
                if [[ "$chosen_size" == "Custom" ]]; then
                  read -p "Enter custom square size: " SQUARE_SIZE
                else
                  SQUARE_SIZE="$chosen_size"
                fi
                echo ""

                # Menu for color scheme
                COLOR_SCHEME=$(get_menu_choice "Choose color scheme: " "${color_scheme_options[@]}")
                echo ""

                # Ask about borders
                read -r -p "Show borders? [y/N] " borders_input
                if [[ "$borders_input" =~ ^[yY] ]]; then
                  BORDERS="yes"
                else
                  BORDERS="no"
                fi
                echo ""

                # Ask about opacity variation (phrased as disabling it)
                read -r -p "Disable opacity variation? [y/N] " opacity_input
                if [[ "$opacity_input" =~ ^[yY] ]]; then
                  OPACITY_VARIATION="no" # User wants to disable it
                else
                  OPACITY_VARIATION="yes" # User wants to keep it enabled (default)
                fi
                echo ""

                # Update Square.json using jq (ensure correct path)
                echo "Updating examples/Square/Square.json..."
                jq ".square_size = $(echo "$SQUARE_SIZE" | bc)" examples/Square/Square.json > tmp.json && mv tmp.json examples/Square/Square.json
                jq ".color_scheme = \"$COLOR_SCHEME\"" examples/Square/Square.json > tmp.json && mv tmp.json examples/Square/Square.json
                jq ".borders = \"$BORDERS\"" examples/Square/Square.json > tmp.json && mv tmp.json examples/Square/Square.json
                jq ".opacity_variation = \"$OPACITY_VARIATION\"" examples/Square/Square.json > tmp.json && mv tmp.json examples/Square/Square.json # Add opacity update
                echo "Configuration updated."
                echo "---------------------------------"
                echo ""
            fi
            # --- End Square specific configuration ---

            # Run the selected tool (runs for all, after Square config if applicable)
            run_tool "$tool_name"
            ;;
        h|help)
            show_help
            ;;
        q|quit|exit)
            echo "Exiting Manim Examples. Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid input. Please enter a number, 'h' for help, or 'q' to quit."
            sleep 1
            ;;
    esac
done
