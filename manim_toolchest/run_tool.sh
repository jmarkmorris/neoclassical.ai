#!/bin/bash

# Function to list available Python files
list_tools() {
  echo "Available tools:"
  ls *.py | grep -v '__init__.py' | sed 's/\.py//' | sed 's/\.py//' | awk '{print "  " NR ") " $1}'
}

# Function to run the selected tool
run_tool() {
  local tool_name="$1"
  echo "Running $tool_name..."
  manim -pqh --disable_caching "$tool_name.py" "$tool_name" -p
}

# Main script
while true; do
  list_tools
  read -p "Enter the number of the tool to run (or 'q' to quit): " choice

  case "$choice" in
    [1-9]*)
      tool_name=$(ls *.py | grep -v '__init__.py' | sed 's/\.py//' | awk "NR==$choice {print \$1}")
      if [ -n "$tool_name" ]; then
        run_tool "$tool_name"
      else
        echo "Invalid selection."
      fi
      ;;
    q|Q)
      echo "Exiting."
      exit 0
      ;;
    *)
      echo "Invalid input. Please enter a number or 'q'."
      ;;
  esac
done
```
