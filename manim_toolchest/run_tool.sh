#!/bin/bash

# Set terminal colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    clear
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║                 MANIM TOOLCHEST LAUNCHER                   ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to list available Python files
list_tools() {
    echo -e "${BLUE}Available tools:${NC}"
    echo ""
    
    # Get all Python files except __init__.py and tools.py
    files=$(ls *.py | grep -v '__init__.py' | grep -v 'tools.py' | sort)
    
    # Calculate the number of columns based on terminal width
    term_width=$(tput cols)
    max_name_length=25
    num_cols=$((term_width / (max_name_length + 5)))
    
    # Ensure at least one column
    if [ $num_cols -lt 1 ]; then
        num_cols=1
    fi
    
    # Count total files
    total_files=$(echo "$files" | wc -l)
    rows_per_col=$(( (total_files + num_cols - 1) / num_cols ))
    
    # Create a temporary file with numbered entries
    temp_file=$(mktemp)
    counter=1
    while read -r file; do
        # Extract class name from file (assuming file name matches class name)
        class_name=${file%.py}
        
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
    echo -e "${YELLOW}Running $tool_name...${NC}"
    echo -e "${GREEN}Command: manim -pqk --disable_caching $tool_name.py $tool_name -p${NC}"
    echo ""
    
    # Run the tool with high quality rendering
    manim -pqk --disable_caching "$tool_name.py" "$tool_name" -p
    
    echo ""
    echo -e "${GREEN}Finished running $tool_name.${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Function to display help
show_help() {
    echo -e "${BLUE}Manim Toolchest Help:${NC}"
    echo ""
    echo "This script allows you to run various Manim animations from the toolchest."
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  [number]   - Run the animation with the corresponding number"
    echo "  h, help    - Display this help message"
    echo "  q, quit    - Exit the program"
    echo ""
    echo -e "${YELLOW}Rendering Options:${NC}"
    echo "  All animations are rendered with high quality (-qk) settings"
    echo "  Preview is automatically shown after rendering"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Main script
while true; do
    print_banner
    list_tools
    echo -e "${YELLOW}Enter the number of the tool to run, 'h' for help, or 'q' to quit:${NC} "
    read -p "> " choice

    case "$choice" in
        [0-9]*)
            tool_name=$(ls *.py | grep -v '__init__.py' | grep -v 'tools.py' | sort | sed -n "${choice}p" | sed 's/\.py//')
            if [ -n "$tool_name" ]; then
                run_tool "$tool_name"
            else
                echo -e "${RED}Invalid selection.${NC}"
                sleep 1
            fi
            ;;
        h|help)
            show_help
            ;;
        q|quit|exit)
            echo -e "${GREEN}Exiting Manim Toolchest. Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid input. Please enter a number, 'h' for help, or 'q' to quit.${NC}"
            sleep 1
            ;;
    esac
done
```
