#!/bin/bash
#
# run-mysettings.sh
#
# This script backs up specific user configuration files to a designated
# directory. It identifies the host type ('air' or 'pro') based
# on the hostname and adjusts the source virtual environment directory
# and destination filenames accordingly.
#
# Files backed up:
# - .bash_profile
# - .bashrc
# - VS Code settings.json
# - venv activate script (from .venv_air or .venv_pro)
#

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error.
set -u
# Ensure pipeline errors are caught.
set -o pipefail
# set -x

# --- Configuration ---
# Use standard $HOME variable for portability
USER_HOME="$HOME"
TARGET_DIR="${USER_HOME}/Documents/NPQG_Code_Base/MySettings"
SEPARATOR="--------------------------------------------------------------------------------" # 80 dashes

# Source file paths
BASH_PROFILE_SRC="${USER_HOME}/.bash_profile"
BASHRC_SRC="${USER_HOME}/.bashrc"
VSCODE_SETTINGS_SRC="${USER_HOME}/Library/Application Support/Code/User/settings.json"
# Virtual environment directory name prefix (suffix added based on host type)
VENV_DIR_PREFIX=".venv_"


# --- Error Handling ---
handle_error() {
  local exit_code=$?
  echo "$SEPARATOR" >&2
  echo "mysettings.sh script finished: FAILURE (Exit Code: $exit_code)" >&2
  # No need to explicitly exit here if trapping ERR with set -e
}
trap handle_error ERR


# --- Functions ---

# Copies a file if the source exists.
# Usage: copy_file_if_exists <source_path> <destination_path> <description>
copy_file_if_exists() {
  local src="$1"
  local dest="$2"
  local desc="$3"

  if [ -f "$src" ]; then
    # Create the target directory path if it doesn't exist
    # Use dirname to get the directory part of the destination path
    mkdir -p "$(dirname "$dest")"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create directory for $dest." >&2
        exit 1 # Exit because we can't proceed without the directory
    fi

    # Perform the copy
    cp "$src" "$dest"
    # set -e handles exit on error, but we add a more specific message if needed
    if [ $? -ne 0 ]; then
      echo "ERROR: Failed to copy $desc from '$src' to '$dest'." >&2
      # set -e will cause script to exit here
    else
      echo "Copied......: $desc"
      echo "  Source: $src"
      echo "  Target: $dest"
    fi
  else
    echo "Warning: $desc source not found at '$src'. Skipping copy."
  fi
}

# --- Main Script ---

echo "$SEPARATOR" # Print separator at the beginning

# Ensure the base target directory exists
echo "Check target directory: $TARGET_DIR"
mkdir -p "$TARGET_DIR"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create base target directory '$TARGET_DIR'." >&2
    exit 1
fi
echo "Target directory check complete."


echo "Checking hostname: $HOSTNAME"

# Determine host type using a case statement for clarity
HOST_TYPE=""
case "$HOSTNAME" in
  *[Aa][Ii][Rr]*)
    HOST_TYPE="air"
    ;;
  *[Pp][Rr][Oo]*)
    HOST_TYPE="pro"
    ;;
  *)
    HOST_TYPE="" # Explicitly set to empty if no match
    ;;
esac

# Proceed only if a known host type is detected
if [ -n "$HOST_TYPE" ]; then
  echo "Hostname contains '$HOST_TYPE'. Copying ${HOST_TYPE}-specific files..."

  # Define host-specific source and destination paths
  VENV_DIR="${VENV_DIR_PREFIX}${HOST_TYPE}" # e.g., .venv_air
  ACTIVATE_SRC="${VENV_DIR}/bin/activate"
  ACTIVATE_DEST="${TARGET_DIR}/${HOST_TYPE}_activate"
  BASH_PROFILE_DEST="${TARGET_DIR}/${HOST_TYPE}.bash_profile"
  BASHRC_DEST="${TARGET_DIR}/${HOST_TYPE}.bashrc"
  SETTINGS_DEST="${TARGET_DIR}/${HOST_TYPE}_settings.json"

  # --- Copy Files ---

  # Copy activate script (special check for directory first)
  if [ -d "$VENV_DIR" ]; then
    copy_file_if_exists "$ACTIVATE_SRC" "$ACTIVATE_DEST" "Activate script"
  else
    echo "Warning: Virtual environment directory '$VENV_DIR' not found. Skipping activate script copy."
  fi

  # Copy other configuration files using the function
  copy_file_if_exists "$BASH_PROFILE_SRC" "$BASH_PROFILE_DEST" "Bash profile"
  copy_file_if_exists "$BASHRC_SRC" "$BASHRC_DEST" "Bashrc"
  copy_file_if_exists "$VSCODE_SETTINGS_SRC" "$SETTINGS_DEST" "VS Code settings"

else
  echo "Hostname does not match 'air' or 'pro'. No host-specific files copied."
fi

echo "$SEPARATOR"
echo "mysettings.sh script finished: SUCCESS"
