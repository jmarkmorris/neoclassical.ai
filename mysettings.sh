#!/bin/bash

# Define target directory and user home for clarity
TARGET_DIR="/Users/markmorris/Documents/NPQG_Code_Base/MySettings"
USER_HOME="/Users/markmorris"

# Ensure the target directory exists
mkdir -p "$TARGET_DIR"

echo "Checking hostname: $HOSTNAME"

if [[ "$HOSTNAME" =~ [Aa][Ii][Rr]] ]; then
  echo "Hostname contains 'air'. Copying mac air-specific files..."

  # Copy activate script if venv exists
  if [ -d ".venv_air" ] && [ -f ".venv_air/bin/activate" ]; then
    cp .venv_air/bin/activate "$TARGET_DIR/air_activate"
    echo "Copied .venv_air/bin/activate to $TARGET_DIR/air_activate"
  else
    echo "Warning: .venv_air/bin/activate not found. Skipping copy."
  fi

  # Copy bash profile if it exists
  if [ -f "$USER_HOME/.bash_profile" ]; then
    cp "$USER_HOME/.bash_profile" "$TARGET_DIR/air.bash_profile"
    echo "Copied $USER_HOME/.bash_profile to $TARGET_DIR/air.bash_profile"
  else
    echo "Warning: $USER_HOME/.bash_profile not found. Skipping copy."
  fi

  # Copy bashrc if it exists
  if [ -f "$USER_HOME/.bashrc" ]; then
    cp "$USER_HOME/.bashrc" "$TARGET_DIR/air.bashrc"
    echo "Copied $USER_HOME/.bashrc to $TARGET_DIR/air.bashrc"
  else
    echo "Warning: $USER_HOME/.bashrc not found. Skipping copy."
  fi

elif [[ "$HOSTNAME" =~ [Pp][Rr][Oo] ]]; then
  echo "Hostname contains 'pro'. Copying mac pro-specific files..."

  # Copy activate script if venv exists
  if [ -d ".venv_pro" ] && [ -f ".venv_pro/bin/activate" ]; then
    cp .venv_pro/bin/activate "$TARGET_DIR/pro_activate"
    echo "Copied .venv_pro/bin/activate to $TARGET_DIR/pro_activate"
  else
    echo "Warning: .venv_pro/bin/activate not found. Skipping copy."
  fi

  # Copy bash profile if it exists
  if [ -f "$USER_HOME/.bash_profile" ]; then
    cp "$USER_HOME/.bash_profile" "$TARGET_DIR/pro.bash_profile"
    echo "Copied $USER_HOME/.bash_profile to $TARGET_DIR/pro.bash_profile"
  else
    echo "Warning: $USER_HOME/.bash_profile not found. Skipping copy."
  fi

  # Copy bashrc if it exists
  if [ -f "$USER_HOME/.bashrc" ]; then
    cp "$USER_HOME/.bashrc" "$TARGET_DIR/pro.bashrc"
    echo "Copied $USER_HOME/.bashrc to $TARGET_DIR/pro.bashrc"
  else
    echo "Warning: $USER_HOME/.bashrc not found. Skipping copy."
  fi

else
  echo "Hostname does not match 'air' or 'pro'. No host-specific files copied."
fi

echo "mysettings.sh script finished."
