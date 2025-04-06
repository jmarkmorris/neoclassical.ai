#!/bin/bash

# File to store API keys
API_KEYS_FILE="$HOME/.llm_api_keys"

# Function to load API keys
load_api_keys() {
    if [ -f "$API_KEYS_FILE" ]; then
        source "$API_KEYS_FILE"
    else
        # Create API keys file if it doesn't exist
        echo "# LLM API Keys Configuration" > "$API_KEYS_FILE"
        echo "OPENAI_API_KEY=\"\"" >> "$API_KEYS_FILE"
        echo "ANTHROPIC_API_KEY=\"\"" >> "$API_KEYS_FILE"
        echo "GOOGLE_API_KEY=\"\"" >> "$API_KEYS_FILE"
        echo "Created API keys file at $API_KEYS_FILE. Please edit it to add your API keys."
        source "$API_KEYS_FILE"
    fi
}

# Function to update an API key
update_api_key() {
    local vendor=$1
    local var_name="${vendor}_API_KEY"
    
    echo -e "Please enter your $vendor API key:"
    read -s api_key
    echo
    
    # Update in-memory variable
    eval "$var_name=\"$api_key\""
    
    # Update the file
    if grep -q "$var_name=" "$API_KEYS_FILE"; then
	sed -i '' "s|$var_name=.*|$var_name=\"$api_key\"|" "$API_KEYS_FILE"
    else
        echo "$var_name=\"$api_key\"" >> "$API_KEYS_FILE"
    fi
    
    echo -e "API key updated successfully!"
}

# Function to display the main menu (accepts mode as $1)
display_main_menu() {
    local mode_label=$( [ "$1" == "architect" ] && echo "Architect Code" || echo "Code" ) # Clarify role in Architect mode
    clear
    echo -e "Step 2: Select LLM Vendor for ${mode_label} Model or Manage Keys"
    echo -e "=============================="
    echo -e "    LLM VENDOR SELECTION     "
    echo -e "=============================="
    echo "1. OpenAI"
    echo "2. Anthropic"
    echo "3. Google"
    echo "4. Update API Keys"
    echo "0. Exit"
    echo -e "=============================="
    echo -n "Enter your choice [1-4, Enter=0]: "
}

# Function to display OpenAI models (accepts role label as $1: "Architect" or "Editor" or "Code")
display_openai_models() {
    local role_label=$1
    clear
    echo -e "Step 3: Select OpenAI ${role_label} Model"
    echo -e "=============================="
    echo -e "      OpenAI MODELS          "
    echo -e "=============================="
    echo "1. gpt-4o"
    echo "2. gpt-4o-mini"
    echo "3. gpt-4-turbo"
    echo "4. gpt-4"
    echo "5. gpt-3.5-turbo"
    echo "0. Back to main menu"
    echo -e "=============================="
    echo -n "Enter your choice [1-5, Enter=0]: "
}

# Function to display Anthropic models (accepts role label as $1: "Architect" or "Editor" or "Code")
display_anthropic_models() {
    local role_label=$1
    clear
    echo -e "Step 3: Select Anthropic ${role_label} Model"
    echo -e "=============================="
    echo -e "      ANTHROPIC MODELS       "
    echo -e "=============================="
    echo "1. claude-3-7-sonnet-20250219"
    echo "2. claude-3-5-haiku-20241022"
    echo "3. claude-3-opus-20240229"
    echo "0. Back to main menu"
    echo -e "=============================="
    echo -n "Enter your choice [1-3, Enter=0]: " # Corrected range
}

# Function to display Google models (accepts role label as $1: "Architect" or "Editor" or "Code")
display_google_models() {
    local role_label=$1
    clear
    echo -e "Step 3: Select Google ${role_label} Model"
    echo -e "=============================="
    echo -e "       GOOGLE MODELS         "
    echo -e "=============================="
    echo "1. gemini/gemini-1.5-pro"
    echo "2. gemini/gemini-2.0-flash"
    echo "3. gemini/gemini-2.0-flash-exp"
    echo "4. gemini/gemini-2.5-pro-exp-03-25"
    echo "5. gemini/gemini-2.5-pro-preview-03-25"
    echo "0. Back to main menu"
    echo -e "=============================="
    echo -n "Enter your choice [1-5, Enter=0]: "
}

# Function to update API keys menu
display_update_api_keys_menu() {
    clear
    echo -e "Manage API Keys"
    echo -e "=============================="
    echo -e "      UPDATE API KEYS        "
    echo -e "=============================="
    echo "1. OpenAI API Key"
    echo "2. Anthropic API Key"
    echo "3. Google API Key"
    echo "0. Back to main menu"
    echo -e "=============================="
    echo -n "Enter your choice [1-3, Enter=0]: "
}

# Function to display the mode selection menu
display_mode_selection_menu() {
    clear
    echo -e "Step 1: Select Operating Mode"
    echo -e "=============================="
    echo -e "      SELECT MODE            "
    echo -e "=============================="
    echo "1. Code Mode"
    echo "2. Architect Mode"
    echo "0. Exit"
    echo -e "=============================="
    echo -n "Enter your choice [1-2, Enter=0]: "
}

# Function to launch aider with potentially different vendors/models for architect and editor
# Usage for Code Mode: launch_aider "code" $vendor $model "" ""
# Usage for Architect Mode: launch_aider "architect" $architect_vendor $architect_model $editor_vendor $editor_model
launch_aider() {
    local mode=$1
    local main_vendor=$2      # Vendor for Code model or Architect model
    local main_model=$3       # Code model or Architect model
    local editor_vendor=$4    # Vendor for Editor model (empty in Code mode)
    local editor_model=$5     # Editor model (empty in Code mode, can be "default" in Architect mode)

    local main_api_key_var="${main_vendor}_API_KEY"
    local main_api_key=$(eval echo \$$main_api_key_var)
    local editor_api_key=""
    local editor_api_key_var=""

    # Check and potentially update main API key
    if [ -z "$main_api_key" ]; then
        echo -e "API key for main vendor ($main_vendor) is not set. Let's update it."
        update_api_key "$main_vendor"
        main_api_key=$(eval echo \$$main_api_key_var)
    fi

    # Base aider command
    local aider_cmd="aider --vim --no-auto-commit"

    # Add main model and its API key flag
    aider_cmd="$aider_cmd --model $main_model"
    case $main_vendor in
        OPENAI)    aider_cmd="$aider_cmd --openai-api-key $main_api_key" ;;
        ANTHROPIC) aider_cmd="$aider_cmd --anthropic-api-key $main_api_key" ;;
        GOOGLE)    aider_cmd="$aider_cmd --api-key google=$main_api_key" ;;
        *) echo "Unknown main vendor: $main_vendor"; return 1 ;;
    esac

    # --- Construct mode-specific arguments ---
    local mode_flag=""
    local editor_model_flag=""
    local mode_display_name=""
    local editor_display_info="" # For the launch message

    if [ "$mode" == "architect" ]; then
        mode_display_name="Architect Mode"
        aider_cmd="$aider_cmd --architect"

        # Add editor model flag and potentially its API key flag
        if [ "$editor_model" != "default" ] && [ -n "$editor_model" ]; then
            aider_cmd="$aider_cmd --editor-model $editor_model"
            editor_display_info=" (Editor: $editor_vendor/$editor_model)"

            # Check if editor vendor is different and handle its API key
            if [ "$editor_vendor" != "$main_vendor" ]; then
                editor_api_key_var="${editor_vendor}_API_KEY"
                editor_api_key=$(eval echo \$$editor_api_key_var)

                if [ -z "$editor_api_key" ]; then
                    echo -e "API key for editor vendor ($editor_vendor) is not set. Let's update it."
                    update_api_key "$editor_vendor"
                    editor_api_key=$(eval echo \$$editor_api_key_var)
                fi

                # Add the specific API key flag for the editor vendor
                case $editor_vendor in
                    OPENAI)    aider_cmd="$aider_cmd --openai-api-key $editor_api_key" ;;
                    ANTHROPIC) aider_cmd="$aider_cmd --anthropic-api-key $editor_api_key" ;;
                    GOOGLE)    aider_cmd="$aider_cmd --api-key google=$editor_api_key" ;;
                    *) echo "Unknown editor vendor: $editor_vendor"; return 1 ;;
                esac
            fi
        else
            editor_display_info=" (Editor: Default)"
        fi

    else # Code mode
        mode_display_name="Code Mode"
        aider_cmd="$aider_cmd --chat-mode code"
    fi

    # Check if aider is installed
    if ! command -v aider &> /dev/null; then
        echo -e "Aider is not installed. Please install it first with:"
        echo "pip install aider-chat"
        read -p "Press Enter to continue..."
        return 1
    fi

    # Launch aider
    echo -e "Launching aider in ${mode_display_name} with $main_vendor/$main_model${editor_display_info}..."
    echo "Command: $aider_cmd"
    echo
    eval $aider_cmd
}

# Main function
main() {
    load_api_keys

    # Select mode first
    local selected_mode=""
    while true; do
        display_mode_selection_menu
        read mode_choice
        case $mode_choice in
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

    # --- Main Selection Loop ---
    while true; do

        # --- Code Mode Logic ---
        if [ "$selected_mode" == "code" ]; then
            display_main_menu "Code"
            read vendor_choice
            case $vendor_choice in
                1) main_vendor="OPENAI" ;;
                2) main_vendor="ANTHROPIC" ;;
                3) main_vendor="GOOGLE" ;;
                4) # Update API Keys (handled below)
                   ;;
                ""|0) echo "Goodbye!"; exit 0 ;;
                *) echo "Invalid choice."; read -p "Press Enter..."; continue ;;
            esac

            if [ "$vendor_choice" == "4" ]; then
                # Handle API Key Update Menu
                while true; do
                    display_update_api_keys_menu
                    read api_choice
                    case $api_choice in
                        1) update_api_key "OPENAI"; ;;
                        2) update_api_key "ANTHROPIC"; ;;
                        3) update_api_key "GOOGLE"; ;;
                        ""|0) break ;; # Back to main menu
                        *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                    esac
                    read -p "Press Enter to return to vendor selection..."
                done
                continue # Go back to vendor selection
            fi

            # Select Code Model from chosen vendor
            while true; do
                case $main_vendor in
                    OPENAI)    display_openai_models "Code" ;;
                    ANTHROPIC) display_anthropic_models "Code" ;;
                    GOOGLE)    display_google_models "Code" ;;
                esac
                read model_choice

                # Assign model based on choice and vendor
                local model_selected=false
                case $main_vendor in
                    OPENAI)
                        case $model_choice in
                            1) main_model="gpt-4o"; model_selected=true ;;
                            2) main_model="gpt-4o-mini"; model_selected=true ;;
                            3) main_model="gpt-4-turbo"; model_selected=true ;;
                            4) main_model="gpt-4"; model_selected=true ;;
                            5) main_model="gpt-3.5-turbo"; model_selected=true ;;
                            ""|0) break ;; # Back to vendor selection
                            *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                        esac ;;
                    ANTHROPIC)
                        case $model_choice in
                            1) main_model="claude-3-7-sonnet-20250219"; model_selected=true ;;
                            2) main_model="claude-3-5-haiku-20241022"; model_selected=true ;;
                            3) main_model="claude-3-opus-20240229"; model_selected=true ;;
                            ""|0) break ;; # Back to vendor selection
                            *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                        esac ;;
                    GOOGLE)
                        case $model_choice in
                            1) main_model="gemini/gemini-1.5-pro"; model_selected=true ;;
                            2) main_model="gemini/gemini-2.0-flash"; model_selected=true ;;
                            3) main_model="gemini/gemini-2.0-flash-exp"; model_selected=true ;;
                            4) main_model="gemini/gemini-2.5-pro-exp-03-25"; model_selected=true ;;
                            5) main_model="gemini/gemini-2.5-pro-preview-03-25"; model_selected=true ;;
                            ""|0) break ;; # Back to vendor selection
                            *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                        esac ;;
                esac

                if $model_selected; then
                    launch_aider "code" "$main_vendor" "$main_model" "" ""
                    exit 0 # Exit script after launch
                fi
            done
            # If loop broken (user chose 0), reset vendor and restart vendor selection
            main_vendor=""
            continue

        # --- Architect Mode Logic ---
        elif [ "$selected_mode" == "architect" ]; then

            # Phase 1: Select Architect Vendor
            if [ -z "$main_vendor" ]; then
                display_main_menu "Architect (Main)"
                read vendor_choice
                case $vendor_choice in
                    1) main_vendor="OPENAI" ;;
                    2) main_vendor="ANTHROPIC" ;;
                    3) main_vendor="GOOGLE" ;;
                    4) # Update API Keys (handled below)
                       ;;
                    ""|0) echo "Goodbye!"; exit 0 ;;
                    *) echo "Invalid choice."; read -p "Press Enter..."; continue ;;
                esac

                if [ "$vendor_choice" == "4" ]; then
                    # Handle API Key Update Menu
                    while true; do
                        display_update_api_keys_menu
                        read api_choice
                        case $api_choice in
                            1) update_api_key "OPENAI"; ;;
                            2) update_api_key "ANTHROPIC"; ;;
                            3) update_api_key "GOOGLE"; ;;
                            ""|0) break ;; # Back to main menu
                            *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                        esac
                        read -p "Press Enter to return to vendor selection..."
                    done
                    continue # Go back to architect vendor selection
                fi
            fi

            # Phase 2: Select Architect Model
            if [ -n "$main_vendor" ] && [ -z "$main_model" ]; then
                 while true; do # Loop for selecting architect model
                    case $main_vendor in
                        OPENAI)    display_openai_models "Architect" ;;
                        ANTHROPIC) display_anthropic_models "Architect" ;;
                        GOOGLE)    display_google_models "Architect" ;;
                    esac
                    read model_choice

                    local model_selected=false
                    case $main_vendor in
                        OPENAI)
                            case $model_choice in
                                1) main_model="gpt-4o"; model_selected=true ;;
                                2) main_model="gpt-4o-mini"; model_selected=true ;;
                                3) main_model="gpt-4-turbo"; model_selected=true ;;
                                4) main_model="gpt-4"; model_selected=true ;;
                                5) main_model="gpt-3.5-turbo"; model_selected=true ;;
                                ""|0) main_vendor=""; break ;; # Back to architect vendor selection
                                *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                            esac ;;
                        ANTHROPIC)
                            case $model_choice in
                                1) main_model="claude-3-7-sonnet-20250219"; model_selected=true ;;
                                2) main_model="claude-3-5-haiku-20241022"; model_selected=true ;;
                                3) main_model="claude-3-opus-20240229"; model_selected=true ;;
                                ""|0) main_vendor=""; break ;; # Back to architect vendor selection
                                *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                            esac ;;
                        GOOGLE)
                            case $model_choice in
                                1) main_model="gemini/gemini-1.5-pro"; model_selected=true ;;
                                2) main_model="gemini/gemini-2.0-flash"; model_selected=true ;;
                                3) main_model="gemini/gemini-2.0-flash-exp"; model_selected=true ;;
                                4) main_model="gemini/gemini-2.5-pro-exp-03-25"; model_selected=true ;;
                                5) main_model="gemini/gemini-2.5-pro-preview-03-25"; model_selected=true ;;
                                ""|0) main_vendor=""; break ;; # Back to architect vendor selection
                                *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                            esac ;;
                    esac
                    if $model_selected || [ -z "$main_vendor" ]; then break; fi # Exit model loop if selected or backed out
                done
                if [ -z "$main_vendor" ]; then continue; fi # Restart main loop if backed out
            fi

            # Phase 3: Select Editor Vendor
            if [ -n "$main_model" ] && [ -z "$editor_vendor" ]; then
                display_main_menu "Editor"
                read vendor_choice
                case $vendor_choice in
                    1) editor_vendor="OPENAI" ;;
                    2) editor_vendor="ANTHROPIC" ;;
                    3) editor_vendor="GOOGLE" ;;
                    4) # Update API Keys (handled below)
                       ;;
                    9) editor_vendor="default"; editor_model="default" ;; # Option 9: Use Default Editor
                    ""|0) main_model=""; main_vendor=""; continue ;; # Back to architect model selection
                    *) echo "Invalid choice."; read -p "Press Enter..."; continue ;;
                esac

                 if [ "$vendor_choice" == "4" ]; then
                    # Handle API Key Update Menu
                    while true; do
                        display_update_api_keys_menu
                        read api_choice
                        case $api_choice in
                            1) update_api_key "OPENAI"; ;;
                            2) update_api_key "ANTHROPIC"; ;;
                            3) update_api_key "GOOGLE"; ;;
                            ""|0) break ;; # Back to main menu
                            *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                        esac
                        read -p "Press Enter to return to vendor selection..."
                    done
                    continue # Go back to editor vendor selection
                fi
            fi

            # Phase 4: Select Editor Model (Skip if default was chosen)
            if [ -n "$editor_vendor" ] && [ "$editor_vendor" != "default" ] && [ -z "$editor_model" ]; then
                 while true; do # Loop for selecting editor model
                    case $editor_vendor in
                        OPENAI)    display_openai_models "Editor" ;;
                        ANTHROPIC) display_anthropic_models "Editor" ;;
                        GOOGLE)    display_google_models "Editor" ;;
                    esac
                    read model_choice

                    local model_selected=false
                    case $editor_vendor in
                        OPENAI)
                            case $model_choice in
                                1) editor_model="gpt-4o"; model_selected=true ;;
                                2) editor_model="gpt-4o-mini"; model_selected=true ;;
                                3) editor_model="gpt-4-turbo"; model_selected=true ;;
                                4) editor_model="gpt-4"; model_selected=true ;;
                                5) editor_model="gpt-3.5-turbo"; model_selected=true ;;
                                ""|0) editor_vendor=""; break ;; # Back to editor vendor selection
                                *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                            esac ;;
                        ANTHROPIC)
                            case $model_choice in
                                1) editor_model="claude-3-7-sonnet-20250219"; model_selected=true ;;
                                2) editor_model="claude-3-5-haiku-20241022"; model_selected=true ;;
                                3) editor_model="claude-3-opus-20240229"; model_selected=true ;;
                                ""|0) editor_vendor=""; break ;; # Back to editor vendor selection
                                *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                            esac ;;
                        GOOGLE)
                            case $model_choice in
                                1) editor_model="gemini/gemini-1.5-pro"; model_selected=true ;;
                                2) editor_model="gemini/gemini-2.0-flash"; model_selected=true ;;
                                3) editor_model="gemini/gemini-2.0-flash-exp"; model_selected=true ;;
                                4) editor_model="gemini/gemini-2.5-pro-exp-03-25"; model_selected=true ;;
                                5) editor_model="gemini/gemini-2.5-pro-preview-03-25"; model_selected=true ;;
                                ""|0) editor_vendor=""; break ;; # Back to editor vendor selection
                                *) echo "Invalid choice."; read -p "Press Enter..."; ;;
                            esac ;;
                    esac
                    if $model_selected || [ -z "$editor_vendor" ]; then break; fi # Exit model loop if selected or backed out
                done
                if [ -z "$editor_vendor" ]; then continue; fi # Restart main loop if backed out
            fi

            # Phase 5: Launch if all architect/editor info is present
            if [ -n "$main_model" ] && [ -n "$editor_model" ]; then
                 launch_aider "architect" "$main_vendor" "$main_model" "$editor_vendor" "$editor_model"
                 exit 0 # Exit script after launch
            fi

        fi # End architect mode logic

        # If we somehow fall through without exiting (e.g., error), loop again
        sleep 1

    done # End Main Selection Loop
}

# Run the main function
main
