#!/bin/bash

# --- Model Definitions ---
# Using indexed arrays for broader bash compatibility
GOOGLE_MODELS=(
    "gemini/gemini-2.5-pro-exp-03-25"
    "gemini/gemini-2.5-pro-preview-03-25"
    "gemini/gemini-2.0-flash-exp"
    "gemini/gemini-2.0-flash"
)
ANTHROPIC_MODELS=(
    "claude-3-7-sonnet-20250219"
    "claude-3-5-haiku-20241022"
)
OPENAI_MODELS=(
    "chatgpt-4o-latest"
    "gpt-4.5-preview"
    "openai/o3-mini"
    "gpt-4o"
    "gpt-4-turbo"
)
DEEPSEEK_MODELS=(
    "deepseek/deepseek-coder"
    "deepseek-reasoner"
    "deepseek/deepseek-reasoner"
    "deepseek/deepseek-chat"
)

# --- Vendor Definitions ---
VENDORS=(
    "GOOGLE"
    "ANTHROPIC"
    "OPENAI"
    "DEEPSEEK"
)

# Parallel array holding the API key flag for each vendor
VENDOR_API_KEY_FLAGS=(
    "api-key google="   # GOOGLE (Note: includes 'google=')
    "anthropic-api-key " # ANTHROPIC (Note the trailing space)
    "openai-api-key "    # OPENAI (Note the trailing space)
    "deepseek-api-key "  # DEEPSEEK (Note the trailing space)
)

# Parallel array to track the source of the API key ("env", "file", or "unset")                                                           
VENDOR_KEY_SOURCE=() # Initialize as empty 

# --- Edit Format Definitions ---
# Define the edit formats used by different modes
ARCHITECT_EDIT_FORMAT="editor-diff"
CODE_EDIT_FORMAT="diff"

# Function to load API keys.
# Priority:
# 1. Environment variables (e.g., OPENAI_API_KEY)
# 2. File specified by PRIMARY_KEYS_FILE env var
# 3. File at $HOME/.llm_api_keys
# Exits with an error if a required key is missing after checking all sources.
#
# Args: None
#
# Outputs:
#   - Exports API key environment variables (e.g., OPENAI_API_KEY) if found.
#   - Populates the global VENDOR_KEY_SOURCE array.
#   - Prints status messages to stdout.
#   - Exits with status 1 if required keys are missing and no keys file is found.
#
# Modifies:
#   - Environment variables for API keys.
#   - VENDOR_KEY_SOURCE array.
load_api_keys() {
    local vendor api_key_var env_api_key key_loaded key_source_msg="" all_keys_loaded_from_env=true

    echo "Attempting to load API keys..."

    # Initialize source array                                                                                                             
    for i in "${!VENDORS[@]}"; do                                                                                                         
        VENDOR_KEY_SOURCE[$i]="unset"                                                                                                     
    done 

    # 1. Check Environment Variables first                                                                                                
    local i=0 # Index for parallel arrays                                                                                                 
    for vendor in "${VENDORS[@]}"; do                                                                                                     
        api_key_var="${vendor}_API_KEY"                                                                                                   
        env_api_key="" # Initialize 

        # --- Special handling for GOOGLE ---
        if [[ "$vendor" == "GOOGLE" ]]; then
            # Prioritize GEMINI_API_KEY if set
            if [ -n "$GEMINI_API_KEY" ]; then
                env_api_key="$GEMINI_API_KEY"
                # echo "Loaded GOOGLE key from GEMINI_API_KEY environment variable." # Optional debug
            # Otherwise, check for GOOGLE_API_KEY
            elif [ -n "$GOOGLE_API_KEY" ]; then
                env_api_key="$GOOGLE_API_KEY"
                # echo "Loaded GOOGLE key from GOOGLE_API_KEY environment variable." # Optional debug
            fi
        else
            # --- Standard handling for other vendors ---
            # Use indirect expansion to get the value of the env var
            env_api_key="${!api_key_var}"
        fi
        # --- End Vendor Specific Handling ---

        if [ -n "$env_api_key" ]; then
            # Key found in environment                                                                                                    
            # Export the variable using the *standard* vendor name (e.g., GOOGLE_API_KEY)                                                 
            # so check_api_key and potentially build_args (if needed) can see it.                                                         
            export "$api_key_var"="$env_api_key"                                                                                          
            VENDOR_KEY_SOURCE[$i]="env" # Mark source as environment                                                                      
            key_source_msg="environment variables" # Update message source if needed                                                      
        else                                                                                                                              
            # Key not found in environment for this vendor                                                                                
            VENDOR_KEY_SOURCE[$i]="unset" # Ensure it's marked as unset                                                                   
            all_keys_loaded_from_env=false                                                                                                
            # Ensure the variable is unset in the script's env if not found in the process env
            # This prevents a previously sourced file's value from persisting incorrectly
            # if the env var is later removed.                                                                                            
            # We still unset the shell variable here to ensure the file source below                                                      
            # doesn't pick up a stale value if the env var was removed but the shell var wasn't cleared.                                  
            unset "$api_key_var"                                                                                                          
        fi                                                                                                                                
        i=$((i + 1)) # Increment index                                                                                                    
    done                                

    if $all_keys_loaded_from_env; then
        echo "All required API keys loaded from environment variables."
        return 0 # Successfully loaded all keys from env
    fi

    # 2. & 3. Check File Locations if not all keys were in env
    local secondary_keys_file="$HOME/.llm_api_keys"
    local keys_file_to_use=""

    if [ -n "$PRIMARY_KEYS_FILE" ] && [ -f "$PRIMARY_KEYS_FILE" ]; then
        keys_file_to_use="$PRIMARY_KEYS_FILE"
        key_source_msg="keys file (PRIMARY_KEYS_FILE): $keys_file_to_use"
    elif [ -f "$secondary_keys_file" ]; then
        keys_file_to_use="$secondary_keys_file"
        key_source_msg="keys file (default): $keys_file_to_use"
    fi

    # Source the file if found (will define/overwrite *_API_KEY vars)
    if [ -n "$keys_file_to_use" ]; then
        echo "Loading API keys from $key_source_msg..."
        # Disable unbound variable errors temporarily during source
        set +u                                                                                                                            
        source "$keys_file_to_use"                                                                                                        
        set -u # Re-enable unbound variable errors                                                                                        
                                                                                                                                          
        # Now, update source for keys that were loaded from the file                                                                      
        local j=0                                                                                                                         
        for vendor_check in "${VENDORS[@]}"; do                                                                                           
            local key_var_check="${vendor_check}_API_KEY"                                                                                 
            local key_val_check="${!key_var_check}" # Check the value *after* sourcing                                                    
            # If source is still unset AND the variable now has a value, it came from the file                                            
            if [[ "${VENDOR_KEY_SOURCE[$j]}" == "unset" && -n "$key_val_check" ]]; then                                                   
                 VENDOR_KEY_SOURCE[$j]="file"                                                                                             
                 # No need to re-export, source already did that.                                                                         
            fi                                                                                                                            
             j=$((j + 1))                                                                                                                 
        done                                                                                                                              
    else                                                                                                                                  
        # No keys file found. Error if keys weren't fully loaded from env.                                                                
        if ! $all_keys_loaded_from_env; then   
             echo "Error: No API keys file found and keys not provided via environment variables."
             echo "Please either:"
             echo "  1. Set environment variables (e.g., export OPENAI_API_KEY=..., export GEMINI_API_KEY=...)"
             echo "  2. Set the PRIMARY_KEYS_FILE environment variable to the full path of your keys file."
             echo "  3. Place your keys file at the default location: '$secondary_keys_file'"
             echo ""
             echo "Example content for the keys file:"
             echo "# LLM API Keys Configuration"
             echo "OPENAI_API_KEY=\"sk-...\""
             echo "ANTHROPIC_API_KEY=\"sk-...\""
             echo "# For Google, use either:"
             echo "GEMINI_API_KEY=\"AIza...\"  # Preferred"
             echo "# GOOGLE_API_KEY=\"AIza...\" # Also supported"
             echo "DEEPSEEK_API_KEY=\"sk-...\""
             exit 1
        fi
    fi
    # If we reached here, keys were loaded either from env, file, or a combination.
    # The check_api_key function will verify if the *specific* needed key is present later.
    echo "API key loading complete (using environment variables and/or file)."
}

# Generalized function to select an entity (vendor or model).
# Args: $1: entity_type (vendor or model)
#       $2: role_label (e.g., "Code", "Architect")
#       $3: vendor (if entity_type is model)
# Output: Sets SELECT_ENTITY_RESULT to the selected entity or "" for back/invalid.
select_entity() {
    local entity_type=$1  # "vendor" or "model"
    local role_label=$2  # "Code", "Architect", or "Editor"
    # local vendor=$3      # Vendor - Moved inside the 'model' block below
    local entities=()    # Use a regular array instead of nameref
    local num_entities
    local choice i         # Added 'i' for loop counter

    if [[ "$entity_type" == "vendor" ]]; then
        entities=("${VENDORS[@]}")
    elif [[ "$entity_type" == "model" ]]; then
        local vendor=$3 # Assign vendor here, only when needed for models
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
        local secondary_keys_file="$HOME/.llm_api_keys" # Define for error message
        echo -e "\nError: API key for $vendor is not set." >&2
        # --- Special error message for GOOGLE ---
        if [[ "$vendor" == "GOOGLE" ]]; then
            echo -e "Please ensure it is defined either as an environment variable (GEMINI_API_KEY or GOOGLE_API_KEY)" >&2
            echo -e "or within your API keys file (GEMINI_API_KEY or GOOGLE_API_KEY)." >&2
            echo -e "Checked locations:" >&2
            echo -e "  - Environment Variable: GEMINI_API_KEY" >&2
            echo -e "  - Environment Variable: GOOGLE_API_KEY" >&2
        else
        # --- Standard error message for other vendors ---
            echo -e "Please ensure it is defined either as an environment variable (${vendor}_API_KEY)" >&2
            echo -e "or within your API keys file." >&2
            echo -e "Checked locations:" >&2
            echo -e "  - Environment Variable: ${vendor}_API_KEY" >&2
        fi
        # --- Common part of error message ---
        if [ -n "$PRIMARY_KEYS_FILE" ]; then
            echo -e "  - Primary Keys File (env): \$PRIMARY_KEYS_FILE -> $PRIMARY_KEYS_FILE" >&2
        else
            echo -e "  - Primary Keys File (env): \$PRIMARY_KEYS_FILE (not set)" >&2
        fi
        echo -e "  - Secondary Keys File (default): $secondary_keys_file" >&2
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
        local key_source="${VENDOR_KEY_SOURCE[$vendor_index]}"                                                                            
        # Only add the API key flag if the key was loaded from a file                                                                     
        if [[ "$key_source" == "file" ]]; then                                                                                            
            local api_key_flag="${VENDOR_API_KEY_FLAGS[$vendor_index]}"                                                                   
            args="$args --${api_key_flag}${main_api_key}"                                                                                 
            # echo "Debug: Adding main API key flag for $main_vendor (source: file)" # Optional debug                                     
        # else                                                                                                                            
            # echo "Debug: Skipping main API key flag for $main_vendor (source: $key_source)" # Optional debug                            
        fi                                                                                                                                
    else                                                                                                                                  
        echo "Error: Unknown main vendor index in _build_main_model_args for: $main_vendor" >&2 
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

        # Check if editor vendor is different from main vendor                                                                            
        if [ "$editor_vendor" != "$main_vendor" ]; then                                                                                   
            # We need the API key value if it came from a file                                                                            
            if [ -n "$editor_api_key" ]; then # editor_api_key is passed only if needed (diff vendor)                                     
                local editor_vendor_index=$(_get_vendor_index "$editor_vendor")                                                           
                if [ "$editor_vendor_index" -ne -1 ]; then                                                                                
                    local editor_key_source="${VENDOR_KEY_SOURCE[$editor_vendor_index]}"                                                  
                    # Only add the API key flag if the key was loaded from a file                                                         
                    if [[ "$editor_key_source" == "file" ]]; then                                                                         
                        local editor_api_key_flag="${VENDOR_API_KEY_FLAGS[$editor_vendor_index]}"                                         
                        args="$args --${editor_api_key_flag}${editor_api_key}"                                                            
                        # echo "Debug: Adding editor API key flag for $editor_vendor (source: file)" # Optional debug                     
                    # else                                                                                                                
                        # echo "Debug: Skipping editor API key flag for $editor_vendor (source: $editor_key_source)" # Optional debug     
                    fi                                                                                                                    
                else                                                                                                                      
                    echo "Error: Unknown editor vendor index in _build_architect_args for: $editor_vendor" >&2  
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
    local aider_cmd="aider --vim --no-auto-commit --read README_prompts.md --read README_ask.md"
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
