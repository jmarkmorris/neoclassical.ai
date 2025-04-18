#!/bin/bash
#set -x

# --- Step 1 & 2: Argument Check ---
# Check if exactly one argument is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 <NewProjectName>"
  echo "Example: $0 DrawBoxes"
  exit 1
fi

# --- Step 3: Store Argument ---
PROJECT_NAME="$1"
TEMPLATE_NAME="MyGodotTemplate"
PROJECT_FILE="project.godot"

# --- Step 4: Navigate to Examples ---
# Assuming the script is run from the repository root (neoclassical.ai)
echo "Changing to examples directory..."
cd examples
if [ $? -ne 0 ]; then
    echo "Error: Failed to change directory to 'examples'. Make sure you are running this script from the repository root."
    exit 1
fi

# Check if template directory exists
if [ ! -d "$TEMPLATE_NAME" ]; then
    echo "Error: Template directory '$TEMPLATE_NAME' not found in 'examples'."
    exit 1
fi

# Check if target project directory already exists
if [ -d "$PROJECT_NAME" ]; then
    echo "Error: Project directory '$PROJECT_NAME' already exists."
    exit 1
fi

# --- Step 5: Copy Template ---
echo "Copying template '$TEMPLATE_NAME' to '$PROJECT_NAME'..."
cp -r "$TEMPLATE_NAME" "$PROJECT_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to copy template directory."
    exit 1
fi

# --- Step 6: Navigate to New Project ---
echo "Changing to new project directory '$PROJECT_NAME'..."
cd "$PROJECT_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to change directory to '$PROJECT_NAME'."
    # Attempt to clean up the partially created project directory
    cd ..
    # rm -rf "$PROJECT_NAME"
    exit 1
fi

# --- Step 7: Modify project.godot ---
echo "Updating '$PROJECT_FILE'..."
if [ ! -f "$PROJECT_FILE" ]; then
    echo "Error: '$PROJECT_FILE' not found in the new project directory."
    # Attempt to clean up
    cd ..
    # rm -rf "$PROJECT_NAME"
    exit 1
fi

# Use sed for in-place replacement. Using '|' as delimiter to avoid issues with '/' in paths/names.
# Note: macOS sed requires an empty string '' after -i for in-place editing without backup.
# Linux sed works with -i without the empty string. This version aims for macOS compatibility.
sed -i '' "s|config/name=\"$TEMPLATE_NAME\"|config/name=\"$PROJECT_NAME\"|" "$PROJECT_FILE"
if [ $? -ne 0 ]; then
    echo "Error: Failed to update '$PROJECT_FILE'."
    # Attempt to clean up
    cd ..
    # rm -rf "$PROJECT_NAME"
    exit 1
fi

# --- Step 8: Success Message ---
echo "-----------------------------------------------------"
echo "Godot project '$PROJECT_NAME' created successfully in 'examples/$PROJECT_NAME'"
echo "-----------------------------------------------------"

exit 0
