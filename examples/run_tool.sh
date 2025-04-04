#!/bin/bash

# Check if we're in the project root directory (where pyproject.toml is)
if [ ! -f "pyproject.toml" ]; then
    echo "Please run this script from the project root directory (the one containing pyproject.toml)"
    echo "Example: cd /path/to/project/root && ./examples/run_tool.sh"
    exit 1
fi

# Print banner
print_banner() {
    clear
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║                 MANIM TOOLCHEST LAUNCHER                   ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
}

# Function to list available Python files
list_tools() {
    echo "Available tools:"
    echo ""
    
    # Get all Python files except __init__.py and tools.py
    # Find Python files within the 'examples' directory
    files=$(find examples -maxdepth 1 -name "*.py" | grep -v '__init__.py' | grep -v 'tools.py' | sort)

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
    while read -r file; do
        # Extract class name from file
        file_basename=$(basename "$file")
        class_name=${file_basename%.py}
        
        # Format the entry with padding
        printf "%3d) %-${max_name_length}s" $counter "$class_name" >> "$temp_file"
        
        # Add newline if we've reached the end of a row
        if [ $((counter % num_cols)) -eq 0 ]; then
            echo "" >> "$temp_file"
        fi
        
        counter=$((counter + 1))
    done <<< "$files"

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
    local script_path="examples/${tool_name}.py" # Construct the path relative to project root
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
    echo "Manim Toolchest Help:"
    echo ""
    echo "This script allows you to run various Manim animations from the toolchest."
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

# Main script
while true; do
    print_banner
    list_tools
    echo "Enter the number of the tool to run, 'h' for help, or 'q' to quit: "
    read -p "> " choice

    case "$choice" in
        [0-9]*)
            # Find the selected file in the 'examples' directory and extract the base name (class name)
            tool_name=$(find examples -maxdepth 1 -name "*.py" | grep -v '__init__.py' | grep -v 'tools.py' | sort | sed -n "${choice}p" | sed 's#.*/##' | sed 's/\.py$//')
            if [ -n "$tool_name" ]; then
                run_tool "$tool_name"
            else
                echo "Invalid selection."
                sleep 1
            fi
            ;;
        h|help)
            show_help
            ;;
        q|quit|exit)
            echo "Exiting Manim Toolchest. Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid input. Please enter a number, 'h' for help, or 'q' to quit."
            sleep 1
            ;;
    esac
done
