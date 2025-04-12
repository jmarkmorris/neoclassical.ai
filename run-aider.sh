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
# Define the specific format strings to use
CODE_DIFF_FORMAT="diff"
CODE_WHOLE_FORMAT="whole"
ARCHITECT_DIFF_FORMAT="editor-diff" # Diff-based format for Architect mode
ARCHITECT_WHOLE_FORMAT="editor-whole" # Whole-based format for Architect mode

# Define the INITIAL default format to use when the script starts
# Set these to your preferred defaults
INITIAL_CODE_FORMAT=$CODE_WHOLE_FORMAT # Or $CODE_DIFF_FORMAT
INITIAL_ARCHITECT_FORMAT=$ARCHITECT_WHOLE_FORMAT # Or $ARCHITECT_DIFF_FORMAT

# --- API Key Loading Helper Functions ---

# Attempts to load API keys from environment variables.
# Updates VENDOR_KEY_SOURCE and exports found keys.
#
# Args: None
#
# Outputs:
#   - Exports API key environment variables (e.g., OPENAI_API_KEY) if found.
#   - Modifies the global VENDOR_KEY_SOURCE array.
#
# Returns:
#   - 0 if all vendor keys were found in the environment.
#   - 1 if one or more keys were not found in the environment.
_load_keys_from_env() {
    local vendor api_key_var env_api_key all_found=true i=0

    echo "Checking environment variables for API keys..."

    for vendor in "${VENDORS[@]}"; do
        api_key_var="${vendor}_API_KEY"
        env_api_key="" # Reset for each vendor

        # --- Special handling for GOOGLE ---
        if [[ "$vendor" == "GOOGLE" ]]; then
            if [ -n "$GEMINI_API_KEY" ]; then
                env_api_key="$GEMINI_API_KEY"
            elif [ -n "$GOOGLE_API_KEY" ]; then
                env_api_key="$GOOGLE_API_KEY"
            fi
        else
            # --- Standard handling for other vendors ---
            env_api_key="${!api_key_var}" # Indirect expansion
        fi
        # --- End Vendor Specific Handling ---

        if [ -n "$env_api_key" ]; then
            # Key found in environment, export the standard var and update source
            export "$api_key_var"="$env_api_key"
            VENDOR_KEY_SOURCE[$i]="env"
            # echo "Debug: Found $vendor key in env." # Optional debug
        else
            # Key not found in environment for this vendor
            VENDOR_KEY_SOURCE[$i]="unset"
            all_found=false
            # Ensure the shell variable is also unset in case it lingered from a previous run/source
            unset "$api_key_var"
            # echo "Debug: Did not find $vendor key in env." # Optional debug
        fi
        i=$((i + 1))
    done

    if $all_found; then
        echo "All required API keys found in environment variables."
        return 0 # Success code (all found)
    else
        echo "One or more API keys not found in environment variables. Will check files."
        return 1 # Failure code (some missing)
    fi
}

# Finds the API keys file to use based on environment variable or default path.
#
# Args: None
#
# Outputs:
#   - Prints the full path of the keys file to stdout if found.
#   - Prints nothing if no suitable file is found.
#
# Returns: None
_find_keys_file() {
    local primary_file="$PRIMARY_KEYS_FILE"
    local secondary_file="$HOME/.llm_api_keys"
    local file_to_use=""

    if [ -n "$primary_file" ] && [ -f "$primary_file" ]; then
        file_to_use="$primary_file"
        # echo "Debug: Using primary keys file: $file_to_use" # Optional debug
    elif [ -f "$secondary_file" ]; then
        file_to_use="$secondary_file"
        # echo "Debug: Using secondary keys file: $file_to_use" # Optional debug
    # else
        # echo "Debug: No API keys file found." # Optional debug
    fi

    # Print the path to stdout if found
    echo "$file_to_use"
}

# Loads API keys from the specified file by sourcing it.
# Updates VENDOR_KEY_SOURCE for keys loaded from the file.
#
# Args:
#   $1: keys_file_path - The full path to the API keys file.
#
# Outputs:
#   - Modifies the global VENDOR_KEY_SOURCE array.
#   - Sources the file, potentially exporting environment variables.
#
# Returns: None
_load_keys_from_file() {
    local keys_file_path=$1
    local j=0 vendor_check key_var_check key_val_check

    if [ ! -f "$keys_file_path" ]; then
        echo "Error: Keys file not found at path: $keys_file_path" >&2
        # This should ideally not happen if _find_keys_file worked, but good practice
        return 1
    fi

    echo "Loading API keys from file: $keys_file_path"
    # Disable unbound variable errors temporarily during source
    set +u
    # shellcheck source=/dev/null # Tell shellcheck we are intentionally sourcing a variable path
    source "$keys_file_path"
    set -u # Re-enable unbound variable errors

    # Update source array for keys that were loaded from the file
    for vendor_check in "${VENDORS[@]}"; do
        key_var_check="${vendor_check}_API_KEY"
        # Check the value *after* sourcing, using indirect expansion
        key_val_check="${!key_var_check}"

        # If source is still unset AND the variable now has a value, it came from the file
        if [[ "${VENDOR_KEY_SOURCE[$j]}" == "unset" && -n "$key_val_check" ]]; then
            VENDOR_KEY_SOURCE[$j]="file"
            # No need to re-export, source should handle that if keys were exported in the file
            # If keys were just assigned (e.g., VAR="value"), export them now
             if ! export -p | grep -q "declare -x ${key_var_check}="; then
                 export "$key_var_check"="$key_val_check"
                 # echo "Debug: Exported $vendor_check key loaded from file." # Optional debug
             fi
        # else
             # echo "Debug: $vendor_check key status unchanged (Source: ${VENDOR_KEY_SOURCE[$j]}, Value present: $( [ -n "$key_val_check" ] && echo true || echo false ))" # Optional debug
        fi
        j=$((j + 1))
    done
}

# --- Main API Key Loading Function ---

# Loads API keys, coordinating checks between environment and files.
# Priority: Environment -> PRIMARY_KEYS_FILE -> $HOME/.llm_api_keys
# Exits with an error if required keys are missing after checking all sources.
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
    local env_load_status keys_file_path

    echo "Attempting to load API keys..."

    # Initialize source array
    local i
    for i in "${!VENDORS[@]}"; do
        VENDOR_KEY_SOURCE[$i]="unset"
    done

    # 1. Try loading from environment variables
    _load_keys_from_env
    env_load_status=$? # Capture return status (0=all found, 1=some missing)

    # 2. If not all keys were in env, try loading from file
    if [ "$env_load_status" -ne 0 ]; then
        keys_file_path=$(_find_keys_file)

        if [ -n "$keys_file_path" ]; then
            # File found, attempt to load from it
            _load_keys_from_file "$keys_file_path"
        else
            # No keys file found, and keys were missing from env. This is an error.
            local secondary_keys_file="$HOME/.llm_api_keys" # Define for error message
            echo "Error: No API keys file found and keys not fully provided via environment variables." >&2
            echo "Please either:" >&2
            echo "  1. Set environment variables for all required vendors (e.g., export OPENAI_API_KEY=..., export GEMINI_API_KEY=...)" >&2
            echo "  2. Set the PRIMARY_KEYS_FILE environment variable to the full path of your keys file." >&2
            echo "  3. Place your keys file at the default location: '$secondary_keys_file'" >&2
            echo "" >&2
            echo "Example content for the keys file:" >&2
            echo "# LLM API Keys Configuration" >&2
            echo "OPENAI_API_KEY=\"sk-...\"" >&2
            echo "ANTHROPIC_API_KEY=\"sk-...\"" >&2
            echo "# For Google, use either:" >&2
            echo "GEMINI_API_KEY=\"AIza...\"  # Preferred" >&2
            echo "# GOOGLE_API_KEY=\"AIza...\" # Also supported" >&2
            echo "DEEPSEEK_API_KEY=\"sk-...\"" >&2
            exit 1
        fi
    fi

    # If we reached here, keys were loaded either from env, file, or a combination.
    # The check_api_key function will verify if the *specific* needed key is present later.
    echo "API key loading process complete."
}


# Generalized function to select an entity (vendor or model) via an interactive menu.
#
# Args:
#   $1: entity_type - The type of entity to select ("vendor" or "model").
#   $2: role_label - A label describing the role for the selection (e.g., "Code", "Architect", "Editor").
#   $3: vendor (optional) - The vendor name, required only when entity_type is "model".
#
# Outputs:
#   - Prints menu options to stdout.
#   - Reads user choice from stdin.
#   - Prints error messages to stderr for invalid input.
#
# Modifies:
#   - Sets the global variable SELECT_ENTITY_RESULT to:
#     - The selected entity name (e.g., "OPENAI", "gpt-4o").
#     - An empty string "" if the user chooses "Back".
#     - "default" if the user chooses "Use same VENDOR and MODEL as Architect" (Editor vendor only).
#     - "invalid" if the user enters an invalid choice.
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
        SELECT_ENTITY_RESULT="invalid" # Set global var on error too
        return 1
    fi

    num_entities=${#entities[@]}

    clear
    local upper_entity_type
    upper_entity_type=$(echo "$entity_type" | tr '[:lower:]' '[:upper:]') # More portable uppercase
    echo -e "Select ${role_label} ${upper_entity_type}: "
    echo -e "====================================="

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
    echo -e "====================================="
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
    # Return 0 for success in setting the global var (or indicating invalid choice)
    return 0
}


# Checks if the API key for the specified vendor is available as an environment variable.
# It relies on load_api_keys having been called previously to load keys from files into env vars if necessary.
#
# Args:
#   $1: vendor - The name of the vendor (e.g., "OPENAI", "GOOGLE").
#
# Outputs:
#   - Prints an error message to stderr and exits with status 1 if the key is not set.
check_api_key() {
    local vendor=$1
    local api_key_var="${vendor}_API_KEY"
    # Use indirect expansion instead of eval
    local api_key="${!api_key_var}"
    local vendor_index=$(_get_vendor_index "$vendor") # Get index for source check
    local key_source="unset" # Default if index is invalid
    if [ "$vendor_index" -ne -1 ]; then
        key_source="${VENDOR_KEY_SOURCE[$vendor_index]}"
    fi

    # Check if the key is actually set *and* its source is known (env or file)
    # This prevents errors if load_api_keys failed silently or VENDOR_KEY_SOURCE is somehow wrong.
    if [ -z "$api_key" ] || [[ "$key_source" == "unset" ]]; then
        local secondary_keys_file="$HOME/.llm_api_keys" # Define for error message
        echo -e "\nError: API key for $vendor is not set or could not be loaded." >&2
        echo -e "Source status: $key_source" >&2 # Add source status to error
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
    # echo "Debug: API key for $vendor confirmed (Source: $key_source)." # Optional debug
}

# Displays the main menu for selecting the aider operating mode (Code/Architect) or exiting.
#
# Args: None
#
# Outputs:
#   - Clears the screen.
#   - Prints the menu options to stdout.
display_mode_selection_menu() {
    clear
    echo -e "Step 1: Select Aider Operating Mode"
    echo -e "====================================="
    echo -e "             SELECT MODE             "
    echo -e "====================================="
    echo "1. Code Mode"
    echo "2. Architect Mode"
    echo "0. Exit"
    echo -e "====================================="
    echo -n "Enter your choice [1-2, Enter=0]: "
}

# --- Helper functions ---

# Gets the numerical index (0-based) of a vendor within the global VENDORS array.
#
# Args:
#   $1: vendor_name - The uppercase name of the vendor (e.g., "OPENAI").
#
# Outputs:
#   - Prints the numerical index to stdout if found.
#   - Prints -1 to stdout if the vendor is not found in the VENDORS array.
_get_vendor_index() {
    local vendor_name=$1
    local index=-1 i
    for i in "${!VENDORS[@]}"; do
        if [[ "${VENDORS[$i]}" == "$vendor_name" ]]; then
            index=$i
            break
        fi
    done
    echo "$index"
}

# Builds the command-line arguments related to the main model selection.
# This includes the --model flag and potentially the vendor-specific API key flag
# if the key was loaded from a file (not from environment variables).
#
# Args:
#   $1: main_vendor - The selected main vendor name.
#   $2: main_model - The selected main model name.
#   $3: main_api_key - The API key value for the main vendor.
#
# Outputs:
#   - Prints the constructed arguments, one per line, to stdout.
#   - Prints error messages to stderr if the vendor index is not found.
# Returns:
#   - 0 on success.
#   - 1 if the vendor index is not found.
_build_main_model_args() {
    local main_vendor=$1
    local main_model=$2
    local main_api_key=$3
    local args_array=() # Use an array to build arguments
    local vendor_index=$(_get_vendor_index "$main_vendor")

    args_array+=("--model" "$main_model")

    if [ "$vendor_index" -ne -1 ]; then
        local key_source="${VENDOR_KEY_SOURCE[$vendor_index]}"
        # Only add the API key flag if the key was loaded from a file
        if [[ "$key_source" == "file" ]]; then
            local flag_def="${VENDOR_API_KEY_FLAGS[$vendor_index]}"
            local flag_name=""
            local key_prefix=""
            # Remove trailing space if exists
            flag_def="${flag_def% }"
            if [[ "$flag_def" == *= ]]; then
                # Ends with '=', split it (e.g., "api-key google=")
                key_prefix="${flag_def#*=}" # Get "google="
                flag_name="${flag_def%=*}"  # Get "api-key"
                args_array+=("--${flag_name}" "${key_prefix}${main_api_key}")
            else
                # No '=', use the whole definition as flag name (e.g., "openai-api-key")
                flag_name="$flag_def"
                args_array+=("--${flag_name}" "$main_api_key")
            fi
            # echo "Debug: Adding main API key flag for $main_vendor (source: file)" # Optional debug
        # else
            # echo "Debug: Skipping main API key flag for $main_vendor (source: $key_source)" # Optional debug
        fi
    else
        echo "Error: Unknown main vendor index in _build_main_model_args for: $main_vendor" >&2
        return 1
    fi

    # Print array elements one per line
    printf "%s\n" "${args_array[@]}"
    return 0
}

# Builds the command-line arguments specific to Architect mode.
# This includes --architect, potentially --editor-model,
# and the editor's API key flag if the editor vendor is different from the main vendor
# and the key was loaded from a file. The --edit-format flag is NOT added here.
#
# Args:
#   $1: editor_vendor - The selected editor vendor name (or "default").
#   $2: editor_model - The selected editor model name (or "default").
#   $3: editor_api_key - The API key value for the editor vendor (only needed if editor_vendor != main_vendor).
#   $4: main_vendor - The selected main vendor name (used for comparison).
#
# Outputs:
#   - Prints the constructed arguments, one per line, to stdout.
#   - Prints error/warning messages to stderr.
# Returns:
#   - 0 on success.
#   - 1 if the editor vendor index is not found when needed.
_build_architect_args() {
    local editor_vendor=$1
    local editor_model=$2
    local editor_api_key=$3
    local main_vendor=$4 # Needed to check if editor vendor differs
    local args_array=() # Use an array to build arguments

    # Always add --architect. Edit format is added in launch_aider.
    args_array+=("--architect")

    # Add --editor-model only if a specific one is chosen (not default)
    if [ "$editor_model" != "default" ] && [ -n "$editor_model" ]; then
        args_array+=("--editor-model" "$editor_model")

        # Check if editor vendor is different from main vendor
        if [ "$editor_vendor" != "$main_vendor" ]; then
            # We need the API key value if it came from a file
            # The key value is passed in $editor_api_key only if needed (diff vendor)
            local editor_vendor_index=$(_get_vendor_index "$editor_vendor")
            if [ "$editor_vendor_index" -ne -1 ]; then
                local editor_key_source="${VENDOR_KEY_SOURCE[$editor_vendor_index]}"
                # Only add the API key flag if the key was loaded from a file
                if [[ "$editor_key_source" == "file" ]]; then
                    # Ensure the key value is actually available before adding the flag
                    if [ -n "$editor_api_key" ]; then
                        local editor_flag_def="${VENDOR_API_KEY_FLAGS[$editor_vendor_index]}"
                        local editor_flag_name=""
                        local editor_key_prefix=""
                        # Remove trailing space if exists
                        editor_flag_def="${editor_flag_def% }"
                        if [[ "$editor_flag_def" == *= ]]; then
                            # Ends with '=', split it
                            editor_key_prefix="${editor_flag_def#*=}"
                            editor_flag_name="${editor_flag_def%=*}"
                            args_array+=("--${editor_flag_name}" "${editor_key_prefix}${editor_api_key}")
                        else
                            # No '=', use the whole definition as flag name
                            editor_flag_name="$editor_flag_def"
                            args_array+=("--${editor_flag_name}" "$editor_api_key")
                        fi
                        # echo "Debug: Adding editor API key flag for $editor_vendor (source: file)" # Optional debug
                    else
                         # This indicates a logic error - key source is file, but key value wasn't passed
                         echo "Warning: Editor key source for $editor_vendor is 'file', but key value is missing in _build_architect_args." >&2
                    fi
                # else
                    # echo "Debug: Skipping editor API key flag for $editor_vendor (source: $editor_key_source)" # Optional debug
                fi
            else
                echo "Error: Unknown editor vendor index in _build_architect_args for: $editor_vendor" >&2
                return 1 # Explicitly return error code
            fi
        fi
    fi

    # Print array elements one per line
    printf "%s\n" "${args_array[@]}"
    return 0
}

# Builds the command-line arguments specific to Code mode.
# Sets the chat mode. The --edit-format flag is NOT added here.
#
# Args: None
#
# Outputs:
#   - Prints the argument string ("--chat-mode", "code"), one per line, to stdout.
_build_code_args() {
    local args_array=("--chat-mode" "code")
    # Print array elements one per line
    printf "%s\n" "${args_array[@]}"
    return 0
}

# --- End Helper functions for launch_aider ---


# Constructs and executes the final aider command based on the selected mode and models.
# Includes a pre-launch confirmation step allowing the user to switch the edit format.
#
# Args:
#   $1: mode - The operating mode ("code" or "architect").
#   $2: main_vendor - The selected main vendor.
#   $3: main_model - The selected main model.
#   $4: editor_vendor - The selected editor vendor (used only in architect mode, can be "default").
#   $5: editor_model - The selected editor model (used only in architect mode, can be "default").
#
# Outputs:
#   - Prints status messages, the pre-launch menu, and the final command to stdout before execution.
#   - Executes the aider command.
#   - Prints error messages to stderr if aider is not found or if the command fails.
# Returns:
#   - 1 if the aider command is not found or if the user chooses to go back.
#   - The exit status of the aider command itself otherwise.
launch_aider() {
    local mode=$1
    local main_vendor=$2
    local main_model=$3
    local editor_vendor=$4
    local editor_model=$5

    local main_api_key_var="${main_vendor}_API_KEY"
    local main_api_key="${!main_api_key_var}" # Get key value using indirect expansion
    local editor_api_key=""
    local editor_api_key_var=""

    # Base aider command parts in an array
    local cmd_array=("aider" "--vim" "--no-auto-commit" "--read" "README-prompts.md" "--read" "README-ask.md")

    # Capture main model args
    local main_args_str
    main_args_str=$(_build_main_model_args "$main_vendor" "$main_model" "$main_api_key")
    if [ $? -ne 0 ]; then return 1; fi # Exit if helper failed
    local main_args_array=()
    mapfile -t main_args_array < <(echo "$main_args_str") # Use mapfile (readarray)
    cmd_array+=("${main_args_array[@]}")

    local mode_args_str
    local mode_args_array=()
    local mode_display_name=""
    local editor_display_info=""
    local actual_format=""
    local alternative_format=""
    local format_constant_base="" # Will be CODE or ARCHITECT

    # Determine initial format and mode-specific args
    if [ "$mode" == "architect" ]; then
        mode_display_name="Architect Mode"
        format_constant_base="ARCHITECT"
        actual_format="$INITIAL_ARCHITECT_FORMAT" # Set initial format

        # Retrieve editor API key value ONLY if editor vendor is different and not default
        # This value is needed by _build_architect_args if the source is 'file'
        if [[ "$editor_vendor" != "$main_vendor" && "$editor_vendor" != "default" && -n "$editor_vendor" ]]; then
             editor_api_key_var="${editor_vendor}_API_KEY"
             editor_api_key="${!editor_api_key_var}" # Get key value using indirect expansion
        fi
        # Get architect-specific args (without edit format)
        # Pass the potentially needed editor_api_key value
        mode_args_str=$(_build_architect_args "$editor_vendor" "$editor_model" "$editor_api_key" "$main_vendor")
        if [ $? -ne 0 ]; then return 1; fi # Exit if helper failed

        # Set editor display info for the menu
        if [[ "$editor_model" != "default" && -n "$editor_model" ]]; then
            editor_display_info=" (Editor: $editor_vendor/$editor_model)"
        else
            editor_display_info=" (Editor: Default)"
        fi
    else # Code mode
        mode_display_name="Code Mode"
        format_constant_base="CODE"
        actual_format="$INITIAL_CODE_FORMAT" # Set initial format
        # Get code-specific args (without edit format)
        mode_args_str=$(_build_code_args)
        if [ $? -ne 0 ]; then return 1; fi # Exit if helper failed
        editor_display_info="" # No editor in code mode
    fi

    # Capture mode args
    mapfile -t mode_args_array < <(echo "$mode_args_str")
    cmd_array+=("${mode_args_array[@]}")

    # Check if aider command exists before entering the loop
    if ! command -v aider &> /dev/null; then
        echo -e "\nError: Aider command not found." >&2
        echo -e "Please ensure 'aider-chat' is installed and in your PATH." >&2
        read -p "Press Enter to return to the main menu..."
        return 1 # Indicate error/abort
    fi

    # Pre-launch confirmation loop
    while true; do
        # --- Determine the alternative format for the menu ---
        local diff_format_var="${format_constant_base}_DIFF_FORMAT"
        local whole_format_var="${format_constant_base}_WHOLE_FORMAT"
        local diff_format="${!diff_format_var}"
        local whole_format="${!whole_format_var}"

        if [[ "$actual_format" == "$diff_format" ]]; then
            alternative_format="$whole_format"
        else
            alternative_format="$diff_format"
        fi

        # --- Build the full command array *for the current format* ---
        # We need to rebuild the array if the format changes
        local current_cmd_array=("${cmd_array[@]}") # Copy base + main + mode args
        current_cmd_array+=("--edit-format" "$actual_format") # Add current format

        # --- Display the pre-launch menu ---
        clear
        echo -e "Launching Aider: ${mode_display_name}"
        echo -e "Main Model:      ${main_vendor}/${main_model}${editor_display_info}"
        echo -e "-------------------------------------"
        echo -e "Current Edit Format: ${actual_format}"
        echo -e "-------------------------------------"
        echo -e "Command to Run:"
        # Print the command array elements, quoted for safety/clarity, and wrap
        printf "%q " "${current_cmd_array[@]}" | fold -s -w "$(tput cols)"
        echo # Add a newline after the command
        echo -e "-------------------------------------"
        echo "1. Launch Aider with this command"
        echo "2. Switch to Format: ${alternative_format}"
        echo "3. Back to Main Menu (Abort Launch)"
        echo -e "-------------------------------------"
        echo -n "Enter choice [1-3, 0=Back, Enter=1]: "
        read confirm_choice

        # --- Handle user choice ---
        case "${confirm_choice:-1}" in # Default to 1 if Enter is pressed
            1)  # Launch
                echo # Newline before execution
                # Execute the command directly using the array
                "${current_cmd_array[@]}"
                local exit_status=$?
                if [ $exit_status -ne 0 ]; then
                    echo "Error: aider command failed with exit status $exit_status." >&2
                    read -p "Press Enter to return to the main menu..."
                fi
                # Whether success or failure, return to main menu after execution attempt
                return $exit_status # Return aider exit status or 0 if successful
                ;;
            2)  # Switch format
                actual_format="$alternative_format"
                # Loop continues, will rebuild command array and redisplay
                continue
                ;;
            3|0)  # Back to Main Menu (Accepts 3 or 0)
                return 1 # Use 1 to indicate user aborted, distinct from aider exit code 0
                ;;
            *)  # Invalid choice
                echo "Invalid choice. Press Enter to try again..." >&2
                read
                # Loop continues
                ;;
        esac
    done
}

# The main entry point and control loop of the script.
# Handles mode selection and calls the appropriate mode-specific function.
#
# Args: None
#
# Outputs:
#   - Calls display_mode_selection_menu to show the mode selection UI.
#   - Reads user input for mode selection.
#   - Prints "Goodbye!" on exit.
#   - Prints error messages for unknown modes.
main() {
    load_api_keys

    # Loop indefinitely until user explicitly exits (choice 0)
    while true; do
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

        # Variables to store selections are now local to the mode functions
        # local main_vendor=""
        # local main_model=""
        # local editor_vendor=""
        # local editor_model="" # Use "default" to signify default editor

        # Call the appropriate function based on selected mode
        if [ "$selected_mode" == "code" ]; then
            run_code_mode  # No arguments needed anymore
        elif [ "$selected_mode" == "architect" ]; then
            run_architect_mode # No arguments needed anymore
        else
            # This case should not be reachable due to the inner loop validation
            echo "Error: Unknown mode selected: $selected_mode" >&2
            exit 1
        fi

        # After run_code_mode or run_architect_mode returns (either after aider runs
        # or the user backs out), the main loop continues, showing the mode selection again.
        # Explicitly continue to ensure the loop restarts correctly.
        continue
    done
}
# Handles the user interaction flow for selecting the vendor and model for Code mode.
# It then calls launch_aider to execute the command.
# Returns control to the main loop after aider exits or if the user selects "Back".
#
# Args: None
#
# Outputs:
#   - Calls select_entity to display menus and get user input.
#   - Calls check_api_key to validate key presence.
#   - Calls launch_aider to run the final command.
#
# Modifies:
#   - Uses and potentially clears local variables main_vendor, main_model.
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
            check_api_key "$main_vendor" # Verify the key is loaded and source is known
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

        # Launch aider (which now includes the confirmation menu)
        # launch_aider returns 0 on successful execution, non-zero on error or user abort (Back)
        launch_aider "code" "$main_vendor" "$main_model" "" ""
        # Regardless of launch_aider return status, we go back to the main menu
        return
    done
}
# Handles the user interaction flow for selecting the main vendor/model and
# editor vendor/model for Architect mode using a linear sequence with validation loops.
# It then calls launch_aider to execute the command.
# Returns control to the main loop after aider exits or if the user selects "Back".
#
# Args: None
#
# Outputs:
#   - Calls select_entity to display menus and get user input.
#   - Calls check_api_key to validate key presence.
#   - Calls launch_aider to run the final command.
#
# Modifies:
#   - Uses and potentially clears local variables main_vendor, main_model,
#     editor_vendor, editor_model.
run_architect_mode() {
    local main_vendor=""
    local main_model=""
    local editor_vendor=""
    local editor_model=""

    # Step 1: Select Main Vendor
    while true; do
        select_entity "vendor" "Architect" # Sets SELECT_ENTITY_RESULT
        if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
            continue # Re-prompt for main vendor
        elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
            return # Back to main menu
        fi
        main_vendor="$SELECT_ENTITY_RESULT"
        check_api_key "$main_vendor" # Verify key is loaded
        break # Vendor selected, exit loop
    done

    # Step 2: Select Main Model
    while true; do
        select_entity "model" "Architect" "$main_vendor" # Sets SELECT_ENTITY_RESULT
        if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
            continue # Re-prompt for main model
        elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
             # Back selected, return to main menu (clearing vendor is not needed as function returns)
            return
        fi
        main_model="$SELECT_ENTITY_RESULT"
        break # Model selected, exit loop
    done

    # Step 3: Select Editor Vendor
    while true; do
        select_entity "vendor" "Editor" # Sets SELECT_ENTITY_RESULT
        if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
            continue # Re-prompt for editor vendor
        elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
            # Back selected, return to main menu
            return
        fi
        editor_vendor="$SELECT_ENTITY_RESULT"
        break # Vendor selected (or "default"), exit loop
    done

    # Step 4: Select Editor Model (or skip if default)
    if [[ "$editor_vendor" == "default" ]]; then
        editor_model="default" # Set model to default as well
    else
        # Specific editor vendor chosen, need to check key and select model
        check_api_key "$editor_vendor" # Verify key is loaded
        while true; do
            select_entity "model" "Editor" "$editor_vendor" # Sets SELECT_ENTITY_RESULT
            if [[ "$SELECT_ENTITY_RESULT" == "invalid" ]]; then
                continue # Re-prompt for editor model
            elif [[ -z "$SELECT_ENTITY_RESULT" ]]; then
                # Back selected, return to main menu
                return
            fi
            editor_model="$SELECT_ENTITY_RESULT"
            break # Model selected, exit loop
        done
    fi

    # Step 5: Launch Aider
    # launch_aider returns 0 on successful execution, non-zero on error or user abort (Back)
    launch_aider "architect" "$main_vendor" "$main_model" "$editor_vendor" "$editor_model"

    # Regardless of launch_aider's return status, we go back to the main menu
    return
}

# Run the main function
main

