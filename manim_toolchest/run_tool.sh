#!/bin/bash

# Check if we're in the manim_toolchest directory
if [ ! -f "$(dirname "$0")/run_tool.sh" ]; then
    echo "Please run this script from the manim_toolchest directory"
    echo "Try: cd manim_toolchest && ./run_tool.sh"
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
    files=$(find . -maxdepth 1 -name "*.py" | grep -v '__init__.py' | grep -v 'tools.py' | sort)
    
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
    local tool_name="$1"
    echo "Running $tool_name..."
    echo "Command: manim -pqk --disable_caching $tool_name.py $tool_name -p"
    echo ""
    
    # Run the tool with high quality rendering
    manim -pqk --disable_caching "$tool_name.py" "$tool_name" -p
    
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
            tool_name=$(find . -maxdepth 1 -name "*.py" | grep -v '__init__.py' | grep -v 'tools.py' | sort | sed -n "${choice}p" | sed 's/\.py$//' | xargs basename)
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
