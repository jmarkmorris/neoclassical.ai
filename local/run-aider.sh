#!/bin/bash

# --- Model Definitions ---
# Using indexed arrays for broader bash compatibility
OPENAI_MODELS=(
    "gpt-4o"
    "gpt-4o-mini"
    "gpt-4-turbo"
    "gpt-4"
    "gpt-3.5-turbo"
)
ANTHROPIC_MODELS=(
    "claude-3-7-sonnet-20250219"
    "claude-3-5-haiku-20241022"
    "claude-3-opus-20240229"
)
GOOGLE_MODELS=(
    "gemini/gemini-1.5-pro"
    "gemini/gemini-2.0-flash"
    "gemini/gemini-2.0-flash-exp"
    "gemini/gemini-2.5-pro-exp-03-25"
    "gemini/gemini-2.5-pro-preview-03-25"
)

# --- Vendor Definitions ---
VENDORS=(
    "OPENAI"
    "ANTHROPIC"
    "GOOGLE"
)

# Parallel array holding the API key flag for each vendor
VENDOR_API_KEY_FLAGS=(
    "openai-api-key "    # OPENAI (Note the trailing space)
    "anthropic-api-key " # ANTHROPIC (Note the trailing space)
    "api-key google="   # GOOGLE (Note: includes 'google=')
)

# --- Edit Format Definitions ---
# Define the edit formats used by different modes
ARCHITECT_EDIT_FORMAT="editor-diff"
CODE_EDIT_FORMAT="diff"

# Function to load API keys from standard locations.
# Checks hardcoded path first, then $HOME/.llm_api_keys.
# Exits with an error if neither file is found.
load_api_keys() {
    # Define potential locations
    local primary_keys_file="/Users/marmorri/Library/CloudStorage/OneDrive-InterSystemsCorporation/MyDesk/.llm_api_keys"
    local secondary_keys_file="$HOME/.llm_api_keys"
    local keys_file_to_use=""

    # Check primary location
    if [ -f "$primary_keys_file" ]; then
        keys_file_to_use="$primary_keys_file"
    # Check secondary location
    elif [ -f "$secondary_keys_file" ]; then
        keys_file_to_use="$secondary_keys_file"
    fi

    # Source the file if found
    if [ -n "$keys_file_to_use" ]; then
        # echo "Loading API keys from: $keys_file_to_use" # Optional debug message
        source "$keys_file_to_use"
    else
        # Neither file found, print error and exit
        echo "Error: API keys file not found."
        echo "Please create '$secondary_keys_file' and add your API keys."
        echo "Example content:"
        echo "# LLM API Keys Configuration"
        echo "OPENAI_API_KEY=\"sk-...\""
        echo "ANTHROPIC_API_KEY=\"sk-...\""
        echo "GOOGLE_API_KEY=\"AIza...\""
        exit 1 # Exit if keys file is missing
    fi
}

# Generalized function to select an entity (vendor or model).
# Args: $1: entity_type (vendor or model)
#       $2: role_label (e.g., "Code", "Architect")
#       $3: vendor (if entity_type is model)
# Output: Sets SELECT_ENTITY_RESULT to the selected entity or "" for back/invalid.
select_entity() {
    local entity_type=$1  # "vendor" or "model"
    local role_label=$2  # "Code", "Architect", or "Editor"
    local vendor=$3      # Vendor (only used if entity_type is "model")
    local entities=()    # Use a regular array instead of nameref
    local num_entities
    local choice i         # Added 'i' for loop counter

    if [[ "$entity_type" == "vendor" ]]; then
        entities=("${VENDORS[@]}")
    elif [[ "$entity_type" == "model" ]]; then
        # Use indirect expansion to dynamically get the correct model array elements
        local models_array_ref="${vendor}_MODELS[@]" # Create reference string including [@]
        # Check if the base array variable exists
        local models_array_name="${vendor}_MODELS"
        if declare -p "$models_array_name" &>/dev/null; then
            # Use indirect expansion to assign elements to the local 'entities' array
            entities=("${!models_array_ref}")
        else
            echo "Error: Model array variable not found for vendor: $vendor" >&2
            # Set result to invalid to prevent proceeding? Or return error code?
            # Let's stick with the global variable pattern for now.
            SELECT_ENTITY_RESULT="invalid"
            return 1 # Return error
        fi
    else
        echo "Error: Invalid entity type: $entity_type" >&2
        return 1
    fi

    num_entities=${#entities[@]}

    clear
    local upper_entity_type
    upper_entity_type=$(echo "$entity_type" | tr '[:lower:]' '[:upper:]') # More portable uppercase
    echo -e "Select ${role_label} ${upper_entity_type}: "
    echo -e "=============================="

    # Use C-style for loop for better compatibility
    for ((i=0; i<num_entities; i++)); do
        printf "%d. %s\n" "$((i + 1))" "${entities[$i]}"
    done
    # Add option 9 only when selecting the Editor vendor
    local prompt_range="1-${num_entities}"
    if [[ "$entity_type" == "vendor" && "$role_label" == "Editor" ]]; then
        echo "9. Use same VENDOR and MODEL as Architect"
        prompt_range="1-${num_entities}, 9"
    fi
    echo "0. Back"
    echo -e "=============================="
    echo -n "Enter your choice [${prompt_range}, Enter=0]: "
    read choice

    SELECT_ENTITY_RESULT=""

    if [[ -z "$choice" || "$choice" == "0" ]]; then
        SELECT_ENTITY_RESULT=""  # "Back" selected
    # Handle option 9 specifically for Editor vendor selection
    elif [[ "$entity_type" == "vendor" && "$role_label" == "Editor" && "$choice" == "9" ]]; then
        SELECT_ENTITY_RESULT="default"
    elif [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= num_entities )); then
        SELECT_ENTITY_RESULT="${entities[$((choice - 1))]}"
    else
        echo "Invalid choice." >&2
        read -p "Press Enter..."
        SELECT_ENTITY_RESULT="invalid"  # Indicate invalid input
    fi
}


# Checks if the API key for the given vendor is set.
# Args: $1: vendor name
# Exits with an error if the key is not set.
check_api_key() {
    local vendor=$1
    local api_key_var="${vendor}_API_KEY"
    # Use indirect expansion instead of eval
    local api_key="${!api_key_var}"

    if [ -z "$api_key" ]; then
        # Reference the standard secondary location in the error message
        local secondary_keys_file="$HOME/.llm_api_keys"
        echo -e "API key for $vendor is not set."
        echo -e "Please ensure it is defined in your API keys file (e.g., '$secondary_keys_file') and try again."
        exit 1
    fi
}

# Displays the menu for selecting the aider operating mode.
display_mode_selection_menu() {
    clear
    echo -e "Step 1: Select Aider Operating Mode"
    echo -e "=============================="
    echo -e "         SELECT MODE          "
    echo -e "=============================="
    echo "1. Code Mode"
    echo "2. Architect Mode"
    echo "0. Exit"
    echo -e "=============================="
    echo -n "Enter your choice [1-2, Enter=0]: "
}

# --- Helper functions ---

# Gets the index of a vendor in the VENDORS array.
# Args: $1: vendor_name (UPPERCASE)
# Returns: The index (0-based) or -1 if not found.
_get_vendor_index() {
    local vendor_name=$1
    local index=-1
    for i in "${!VENDORS[@]}"; do
        if [[ "${VENDORS[$i]}" == "$vendor_name" ]]; then
            index=$i
            break
        fi
    done
    echo "$index"
}

# Builds the command-line arguments for the main model (Code or Architect).
# Args: $1: main_vendor
#       $2: main_model
#       $3: main_api_key
# Returns: The argument string.
_build_main_model_args() {
    local main_vendor=$1
    local main_model=$2
    local main_api_key=$3
    local args=""
    local vendor_index=$(_get_vendor_index "$main_vendor")

    args="$args --model $main_model"

    if [ "$vendor_index" -ne -1 ]; then
        local api_key_flag="${VENDOR_API_KEY_FLAGS[$vendor_index]}"
        # Special handling for Google's format might be needed if the flag didn't include 'google='
        # but since it does, this should work directly.
        args="$args --${api_key_flag}${main_api_key}"
    else
        echo "Error: Unknown main vendor in _build_main_model_args: $main_vendor" >&2
        return 1
    fi

    echo "$args"
}

# Builds the command-line arguments specific to Architect mode.
# Args: $1: editor_vendor
#       $2: editor_model
#       $3: editor_api_key
#       $4: main_vendor
# Returns: The argument string.
_build_architect_args() {
    local editor_vendor=$1
    local editor_model=$2
    local editor_api_key=$3
    local main_vendor=$4 # Needed to check if editor vendor differs
    # Always add --architect and the defined edit format for architect mode
    local args="--architect --edit-format ${ARCHITECT_EDIT_FORMAT}" # Use constant
    # editor_display_info is handled in launch_aider, removed from here

    # Add --editor-model only if a specific one is chosen (not default)
    if [ "$editor_model" != "default" ] && [ -n "$editor_model" ]; then
        args="$args --editor-model $editor_model"
        # editor_display_info=" (Editor: $editor_vendor/$editor_model) --edit-format editor-diff" # Removed

        # Check if editor vendor is different and add its API key flag
        if [ "$editor_vendor" != "$main_vendor" ]; then
            # API key check/update is still in launch_aider for now
            if [ -n "$editor_api_key" ]; then
                local editor_vendor_index=$(_get_vendor_index "$editor_vendor")
                if [ "$editor_vendor_index" -ne -1 ]; then
                    local editor_api_key_flag="${VENDOR_API_KEY_FLAGS[$editor_vendor_index]}"
                    args="$args --${editor_api_key_flag}${editor_api_key}"
                else
                    echo "Error: Unknown editor vendor in _build_architect_args: $editor_vendor" >&2
                    return 1 # Explicitly return error code
                fi
            else
                # This case should ideally be handled before calling launch_aider (Step 2)
                echo "Warning: Editor API key for $editor_vendor not provided to _build_architect_args" >&2
            fi
        fi
    # else
        # editor_display_info=" (Editor: Default)" # Removed
    fi
    # Echo args and display info separately? Or combine? Let's echo args for now.
    # The display info needs to be handled differently, maybe return it too?
    # For now, just echo the command args. Display info logic remains in launch_aider.
    echo "$args"
}

# Builds the command-line arguments specific to Code mode.
# Args: None
# Returns: The argument string.
_build_code_args() {
    echo "--chat-mode code --edit-format ${CODE_EDIT_FORMAT}"
}

# --- End Helper functions for launch_aider ---


# Launches aider with the specified mode, vendors, and models.
# Args: $1: mode (code or architect)
#       $2: main_vendor
#       $3: main_model
#       $4: editor_vendor (for architect mode)
#       $5: editor_model (for architect mode)
launch_aider() {
    local mode=$1
    local main_vendor=$2
    local main_model=$3
    local editor_vendor=$4
    local editor_model=$5

    local main_api_key_var="${main_vendor}_API_KEY"
    # Use indirect expansion instead of eval
    local main_api_key="${!main_api_key_var}"
    local editor_api_key="" # Initialize editor_api_key
    local editor_api_key_var=""

    # Base aider command
    local aider_cmd="aider --vim --no-auto-commit"
    local mode_display_name=""
    local editor_display_info=""

    local main_args=$(_build_main_model_args "$main_vendor" "$main_model" "$main_api_key")
    aider_cmd="$aider_cmd $main_args"

    if [ "$mode" == "architect" ]; then
        mode_display_name="Architect Mode"

        # Retrieve editor API key ONLY if editor vendor is different from main vendor
        if [[ "$editor_vendor" != "$main_vendor" && "$editor_vendor" != "default" && -n "$editor_vendor" ]]; then
             editor_api_key_var="${editor_vendor}_API_KEY"
             editor_api_key="${!editor_api_key_var}"
             # We rely on check_api_key having already validated this key exists
        fi

        # Pass the potentially retrieved editor_api_key to the build function
        local architect_args=$(_build_architect_args "$editor_vendor" "$editor_model" "$editor_api_key" "$main_vendor")
        aider_cmd="$aider_cmd $architect_args"

        if [[ "$editor_model" != "default" && -n "$editor_model" ]]; then
            editor_display_info=" (Editor: $editor_vendor/$editor_model)"
        else
            editor_display_info=" (Editor: Default)"
        fi
    else
        mode_display_name="Code Mode"
        local code_args=$(_build_code_args)
        aider_cmd="$aider_cmd $code_args"
    fi

    if ! command -v aider &> /dev/null; then
        echo -e "Aider is not installed. Please install it first with:"
        echo "pip install aider-chat"
        read -p "Press Enter to continue..."
        return 1
    fi

    echo -e "Launching aider in ${mode_display_name} with ${main_vendor}/${main_model}${editor_display_info}..."
    echo "Command: $aider_cmd"
    echo
    eval "$aider_cmd"
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "Error: aider command failed with exit status $exit_status." >&2
        # Optionally add a pause or specific handling here
        read -p "Press Enter to return to the main menu..."
    fi
    # Function will return normally after this, leading back to the main menu loop.
}

# The main function of the script.
main() {
    load_api_keys

    # Select mode first
    local selected_mode=""
    while true; do
        display_mode_selection_menu
        read mode_choice
        case "$mode_choice" in
            1) selected_mode="code"; break ;;
            2) selected_mode="architect"; break ;;
            ""|0) echo "Goodbye!"; exit 0 ;; # Treat Enter as 0
            *) echo "Invalid choice. Press Enter to continue..."; read ;;
        esac
    done

    # Variables to store selections
    local main_vendor=""
    local main_model=""
    local editor_vendor=""
    local editor_model="" # Use "default" to signify default editor

    # Call the appropriate function based on selected mode
    if [ "$selected_mode" == "code" ]; then
        run_code_mode  # No arguments needed anymore
    elif [ "$selected_mode" == "architect" ]; then
        run_architect_mode # No arguments needed anymore
    else
        echo "Error: Unknown mode selected: $selected_mode"
        exit 1
    fi

    # After run_code_mode or run_architect_mode returns, the loop continues,
    # effectively showing the mode selection menu again.
    # The only clean exit is choosing '0' from the mode selection menu.
}
# Runs aider in Code mode using a linear flow.
# Returns control to the caller (main loop) when done or when 'back' is selected from vendor choice.
run_code_mode() {
    local main_vendor=""
    local main_model=""

    # Removed local selection variable

    # Single loop to manage vendor and model selection state
    while true; do
        # Step 1: Select Vendor (if not already selected)
        if [ -z "$main_vendor" ]; then
            select_entity "vendor" "Code" # Sets SELECT_ENTITY_RESULT
            if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
                continue # Loop back to re-select vendor
            elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
                # User selected "Back" from vendor selection (empty string)
                return # Return to main menu
            fi
            # Vendor selected successfully
            main_vendor="$SELECT_ENTITY_RESULT"
            check_api_key "$main_vendor"
            # Continue within the same loop iteration to select model
        fi

        # Step 2: Select Model (requires vendor to be selected)
        select_entity "model" "Code" "$main_vendor" # Sets SELECT_ENTITY_RESULT
        if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
            continue # Loop back to re-select model (vendor remains selected)
        elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
            # User selected "Back" from model selection (empty string)
            main_vendor="" # Clear vendor selection
            continue      # Loop back, will prompt for vendor again
        fi
        # Model selected successfully
        main_model="$SELECT_ENTITY_RESULT"

        # Launch aider and then return to the main menu loop
        launch_aider "code" "$main_vendor" "$main_model" "" ""
        return # Return control to the main loop
    done
}
# Runs aider in Architect mode using a state machine.
# Returns control to the caller (main loop) when done or when 'back' is selected from the initial vendor choice.
run_architect_mode() {
    local main_vendor=""
    local main_model=""
    local editor_vendor=""
    local editor_model=""
    # Removed local selection variable

    # State machine flow: vendor -> model -> editor_vendor -> editor_model -> launch
    local current_step="select_main_vendor"

    while true; do
        case "$current_step" in
            "select_main_vendor")
                select_entity "vendor" "Architect" # Sets SELECT_ENTITY_RESULT
                if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
                    continue
                elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
                    # User selected "Back" (empty string)
                    return # Back to main menu
                fi
                main_vendor="$SELECT_ENTITY_RESULT"
                check_api_key "$main_vendor"
                current_step="select_main_model"
                ;;

            "select_main_model")
                select_entity "model" "Architect" "$main_vendor" # Sets SELECT_ENTITY_RESULT
                if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
                    continue
                elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
                    # User selected "Back" (empty string)
                    main_vendor="" # Clear selection
                    current_step="select_main_vendor" # Go back to previous step
                    continue
                fi
                main_model="$SELECT_ENTITY_RESULT"
                current_step="select_editor_vendor"
                ;;

            "select_editor_vendor")
                select_entity "vendor" "Editor" # Sets SELECT_ENTITY_RESULT
                if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
                    continue
                elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
                     # User selected "Back" (empty string)
                    main_model="" # Clear selection
                    current_step="select_main_model" # Go back to previous step
                    continue
                fi
                editor_vendor="$SELECT_ENTITY_RESULT"

                # Handle the "default" selection from select_entity
                if [[ "$editor_vendor" == "default" ]]; then
                   editor_model="default" # Also set model to default
                   current_step="launch"  # Skip editor model selection and key check
                   continue               # Go directly to launch state
                fi

                # If not default, proceed to check key and select model
                check_api_key "$editor_vendor"
                current_step="select_editor_model"
                ;;

            "select_editor_model")
                select_entity "model" "Editor" "$editor_vendor" # Sets SELECT_ENTITY_RESULT
                if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
                    continue
                elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
                    # User selected "Back" (empty string)
                    editor_vendor="" # Clear selection
                    current_step="select_editor_vendor" # Go back to previous step
                    continue
                fi
                editor_model="$SELECT_ENTITY_RESULT"
                current_step="launch"
                ;;

            "launch")
                # Handle the case where editor vendor wasn't selected (e.g., if default was chosen)
                # This logic assumes editor_vendor and editor_model are set appropriately before reaching here.
                # If we add a "default" option earlier, this needs adjustment.
                launch_aider "architect" "$main_vendor" "$main_model" "$editor_vendor" "$editor_model"
                return # Return control to the main loop
                ;;

            *) # Should not happen
                echo "Error: Invalid state in run_architect_mode: $current_step" >&2
                exit 1
                ;;
        esac
    done
}

# Run the main function
main
