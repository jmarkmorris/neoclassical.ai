#!/bin/bash
# set -x

# Define target directory relative to user home
# Use standard $HOME variable for portability
USER_HOME="$HOME"
TARGET_DIR="${USER_HOME}/Users/markmorris/Documents/NPQG_Code_Base/MySettings"


# Ensure the target directory exists
mkdir -p "$TARGET_DIR"

echo "Checking hostname: $HOSTNAME"

# Determine host type
HOST_TYPE=""
if [[ "$HOSTNAME" =~ [Aa][Ii][Rr] ]]; then
  HOST_TYPE="air"
elif [[ "$HOSTNAME" =~ [Pp][Rr][Oo] ]]; then
  HOST_TYPE="pro"
fi

# Proceed only if a known host type is detected
if [ -n "$HOST_TYPE" ]; then
  echo "Hostname contains '$HOST_TYPE'. Copying ${HOST_TYPE}-specific files..."

  # Define source and destination paths based on host type
  VENV_DIR=".venv_${HOST_TYPE}"
  ACTIVATE_SRC="${VENV_DIR}/bin/activate"
  ACTIVATE_DEST="${TARGET_DIR}/${HOST_TYPE}_activate"

  # Source paths should use $USER_HOME (which is now $HOME)
  BASH_PROFILE_SRC="${USER_HOME}/.bash_profile"
  BASH_PROFILE_DEST="${TARGET_DIR}/${HOST_TYPE}.bash_profile"

  BASHRC_SRC="${USER_HOME}/.bashrc"
  BASHRC_DEST="${TARGET_DIR}/${HOST_TYPE}.bashrc"

  SETTINGS_SRC="${USER_HOME}/Library/Application Support/Code/User/settings.json"
  SETTINGS_DEST="${TARGET_DIR}/${HOST_TYPE}_settings.json"

  # --- Common Copy Logic ---

  # Copy activate script if venv and activate script exist
  if [ -d "$VENV_DIR" ] && [ -f "$ACTIVATE_SRC" ]; then
    cp "$ACTIVATE_SRC" "$ACTIVATE_DEST"
    echo "Copied $ACTIVATE_SRC to $ACTIVATE_DEST"
  else
    # More specific warning based on which check failed might be useful
    if [ ! -d "$VENV_DIR" ]; then
        echo "Warning: Directory $VENV_DIR not found. Skipping activate script copy."
    elif [ ! -f "$ACTIVATE_SRC" ]; then
        echo "Warning: File $ACTIVATE_SRC not found. Skipping activate script copy."
    fi
  fi

  # Copy bash profile if it exists
  if [ -f "$BASH_PROFILE_SRC" ]; then
    cp "$BASH_PROFILE_SRC" "$BASH_PROFILE_DEST"
    echo "Copied $BASH_PROFILE_SRC to $BASH_PROFILE_DEST"
  else
    echo "Warning: $BASH_PROFILE_SRC not found. Skipping copy."
  fi

  # Copy bashrc if it exists
  if [ -f "$BASHRC_SRC" ]; then
    cp "$BASHRC_SRC" "$BASHRC_DEST"
    echo "Copied $BASHRC_SRC to $BASHRC_DEST"
  else
    echo "Warning: $BASHRC_SRC not found. Skipping copy."
  fi

    # Copy VS Code settings if it exists
  if [ -f "$SETTINGS_SRC" ]; then
    cp "$SETTINGS_SRC" "$SETTINGS_DEST"
    echo "Copied $SETTINGS_SRC to $SETTINGS_DEST"
  else
    echo "Warning: $SETTINGS_SRC not found. Skipping copy."
  fi

else
  echo "Hostname does not match 'air' or 'pro'. No host-specific files copied."
fi

echo "mysettings.sh script finished."
