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
    local mode_label=$( [ "$1" == "architect" ] && echo "Architect Code Model" || echo "Code Model" ) # Clarify role in Architect mode and add 'Model' to Code
    clear
    echo -e "Step 2: Select LLM Vendor for ${mode_label} or Manage Keys" # Removed duplicate 'Model' here
    echo -e "=============================="
    echo -e "    LLM VENDOR SELECTION     "
    echo -e "=============================="
    echo "1. OpenAI"
    echo "2. Anthropic"
    echo "3. Google"
    echo "4. Update API Keys"
    echo "0. Exit"
    echo -e "=============================="
    echo -n "Enter your choice [0-4]: "
}

# Function to display OpenAI models (accepts mode as $1)
display_openai_models() {
    local mode_label=$( [ "$1" == "architect" ] && echo "Architect" || echo "Code" )
    clear
    echo -e "Step 3: Select OpenAI ${mode_label} Model"
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
    echo -n "Enter your choice [0-5]: "
}

# Function to display Anthropic models (accepts mode as $1)
display_anthropic_models() {
    local mode_label=$( [ "$1" == "architect" ] && echo "Architect" || echo "Code" )
    clear
    echo -e "Step 3: Select Anthropic ${mode_label} Model"
    echo -e "=============================="
    echo -e "      ANTHROPIC MODELS       "
    echo -e "=============================="
    echo "1. claude-3-7-sonnet-20250219"
    echo "2. claude-3-5-haiku-20241022"
    echo "3. claude-3-opus-20240229"
    echo "0. Back to main menu"
    echo -e "=============================="
    echo -n "Enter your choice [0-6]: "
}

# Function to display Google models (accepts mode as $1)
display_google_models() {
    local mode_label=$( [ "$1" == "architect" ] && echo "Architect" || echo "Code" )
    clear
    echo -e "Step 3: Select Google ${mode_label} Model"
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
    echo -n "Enter your choice [0-5]: "
}

# Function to display OpenAI editor models
display_openai_editor_models() {
    clear
    echo -e "Step 4 (Architect Mode Only): Select OpenAI Editor Model"
    echo -e "=============================="
    echo -e "   SELECT OpenAI EDITOR MODEL "
    echo -e "=============================="
    echo "1. gpt-4o"
    echo "2. gpt-4o-mini"
    echo "3. gpt-4-turbo"
    echo "4. gpt-4"
    echo "5. gpt-3.5-turbo"
    echo "9. Use Default Editor"
    echo "0. Back to OpenAI Models"
    echo -e "=============================="
    echo -n "Enter your choice [0-5, 9]: "
}

# Function to display Anthropic editor models
display_anthropic_editor_models() {
    clear
    echo -e "Step 4 (Architect Mode Only): Select Anthropic Editor Model"
    echo -e "=============================="
    echo -e "  SELECT ANTHROPIC EDITOR MODEL "
    echo -e "=============================="
    echo "1. claude-3-7-sonnet-20250219"
    echo "2. claude-3-5-haiku-20241022"
    echo "3. claude-3-opus-20240229"
    echo "9. Use Default Editor"
    echo "0. Back to Anthropic Models"
    echo -e "=============================="
    echo -n "Enter your choice [0-3, 9]: "
}

# Function to display Google editor models
display_google_editor_models() {
    clear
    echo -e "Step 4 (Architect Mode Only): Select Google Editor Model"
    echo -e "=============================="
    echo -e "    SELECT GOOGLE EDITOR MODEL  "
    echo -e "=============================="
    echo "1. gemini/gemini-1.5-pro"
    echo "2. gemini/gemini-2.0-flash"
    echo "3. gemini/gemini-2.0-flash-exp"
    echo "4. gemini/gemini-2.5-pro-exp-03-25"
    echo "5. gemini/gemini-2.5-pro-preview-03-25"
    echo "9. Use Default Editor"
    echo "0. Back to Google Models"
    echo -e "=============================="
    echo -n "Enter your choice [0-5, 9]: "
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
    echo -n "Enter your choice [0-3]: "
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
    echo -n "Enter your choice [0-2]: "
}

# Function to launch aider with the selected model, mode, and editor model
launch_aider() {
    local vendor=$1
    local model=$2
    local mode=$3
    local editor_model=$4 # Added editor_model parameter
    local api_key_var="${vendor}_API_KEY"
    local api_key=$(eval echo \$$api_key_var)

    # Check if API key is set
    if [ -z "$api_key" ]; then
        echo -e "API key for $vendor is not set. Let's update it."
        update_api_key $vendor
        api_key=$(eval echo \$$api_key_var)
    fi

    # Prepare aider command based on vendor
    case $vendor in
        OPENAI)
            export OPENAI_API_KEY="$api_key"
            aider_cmd="aider --vim --no-auto-commit --openai-api-key $api_key --model $model"
            ;;
        ANTHROPIC)
            export ANTHROPIC_API_KEY="$api_key"
            aider_cmd="aider --vim --no-auto-commit --anthropic-api-key $api_key --model $model"
            ;;
        GOOGLE)
            export GOOGLE_API_KEY="$api_key"
            aider_cmd="aider --vim --no-auto-commit --api-key google=$api_key --model $model"
            ;;
        *)
            echo "Unknown vendor: $vendor"
            return 1
            ;;
    esac

    # --- Construct aider command arguments ---

    # Add mode flag and potentially editor model flag
    local mode_flag=""
    local editor_model_flag=""
    local mode_display_name=""
    local editor_display_name=""

    if [ "$mode" == "architect" ]; then
        mode_flag="--architect"
        mode_display_name="Architect Mode"
        # Add editor model flag only if not default
        if [ "$editor_model" != "default" ] && [ -n "$editor_model" ]; then
             editor_model_flag="--editor-model $editor_model"
             editor_display_name=" (Editor: $editor_model)"
        else
             editor_display_name=" (Editor: Default)"
        fi
    else # Default to code mode
        mode_flag="--chat-mode code"
        mode_display_name="Code Mode"
    fi
    # Append the mode flag (--chat-mode code or --architect)
    # Append the editor model flag (--editor-model <model>) only if in architect mode and a specific editor was chosen
    aider_cmd="$aider_cmd $mode_flag $editor_model_flag"

    # Check if aider is installed
    if ! command -v aider &> /dev/null; then
        echo -e "Aider is not installed. Please install it first with:"
        echo "pip install aider-chat"
        read -p "Press Enter to continue..."
        return 1
    fi

    # Launch aider
    echo -e "Launching aider in ${mode_display_name} with $model${editor_display_name}..."
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
            0) echo "Goodbye!"; exit 0 ;;
            *) echo "Invalid choice. Press Enter to continue..."; read ;;
        esac
    done

    # Existing vendor/model selection loop
    while true; do
        display_main_menu "$selected_mode" # Pass mode
        read choice
        case $choice in
            1) # OpenAI
                while true; do
                    display_openai_models "$selected_mode" # Pass mode
                    read model_choice
                    local model=""
                    local selected_editor_model="default" # Default value

                    case $model_choice in
                        1) model="gpt-4o" ;;
                        2) model="gpt-4o-mini" ;;
                        3) model="gpt-4-turbo" ;;
                        4) model="gpt-4" ;;
                        5) model="gpt-3.5-turbo" ;;
                        0) break ;; # Back to main menu
                        *) echo "Invalid choice. Press Enter to continue..."; read; continue ;; # Continue OpenAI loop
                    esac # END Main model selection case

                    # If architect mode, select editor model
                    if [ "$selected_mode" == "architect" ]; then
                        while true; do
                            display_openai_editor_models
                            read editor_choice
                            case $editor_choice in
                                1) selected_editor_model="gpt-4o"; break ;;
                                2) selected_editor_model="gpt-4o-mini"; break ;;
                                3) selected_editor_model="gpt-4-turbo"; break ;;
                                4) selected_editor_model="gpt-4"; break ;;
                                5) selected_editor_model="gpt-3.5-turbo"; break ;;
                                9) selected_editor_model="default"; break ;; # Explicitly default
                                0) model=""; break ;; # Go back to selecting main OpenAI model
                                *) echo "Invalid choice. Press Enter to continue..."; read ;;
                            esac
                        done
                        # If user chose 'Back' (model is empty), restart main model selection
                        if [ -z "$model" ]; then continue; fi
                    fi

                    # Launch aider if a model was selected
                    if [ -n "$model" ]; then
                        launch_aider "OPENAI" "$model" "$selected_mode" "$selected_editor_model"
                        break # Break OpenAI loop after launch
                    fi
                done
                ;;
                
            2) # Anthropic
                while true; do
                    display_anthropic_models "$selected_mode" # Pass mode
                    read model_choice
                    local model=""
                    local selected_editor_model="default" # Default value

                    case $model_choice in
                        1) model="claude-3-7-sonnet-20250219" ;;
                        2) model="claude-3-5-haiku-20241022" ;;
                        3) model="claude-3-opus-20240229" ;;
                        0) break ;; # Back to main menu
                        *) echo "Invalid choice. Press Enter to continue..."; read; continue ;; # Continue Anthropic loop
                    esac # END Main model selection case

                    # If architect mode, select editor model
                    if [ "$selected_mode" == "architect" ]; then
                        while true; do
                            display_anthropic_editor_models
                            read editor_choice
                            case $editor_choice in
                                1) selected_editor_model="claude-3-7-sonnet-20250219"; break ;;
                                2) selected_editor_model="claude-3-5-haiku-20241022"; break ;;
                                3) selected_editor_model="claude-3-opus-20240229"; break ;;
                                9) selected_editor_model="default"; break ;; # Explicitly default
                                0) model=""; break ;; # Go back to selecting main Anthropic model
                                *) echo "Invalid choice. Press Enter to continue..."; read ;;
                            esac
                        done
                        # If user chose 'Back' (model is empty), restart main model selection
                        if [ -z "$model" ]; then continue; fi
                    fi

                    # Launch aider if a model was selected
                    if [ -n "$model" ]; then
                        launch_aider "ANTHROPIC" "$model" "$selected_mode" "$selected_editor_model"
                        break # Break Anthropic loop after launch
                    fi
                done
                ;;
                
            3) # Google
                while true; do
                    display_google_models "$selected_mode" # Pass mode
                    read model_choice
                    local model=""
                    local selected_editor_model="default" # Default value

                    case $model_choice in
                        1) model="gemini/gemini-1.5-pro" ;;
                        2) model="gemini/gemini-2.0-flash" ;;
                        3) model="gemini/gemini-2.0-flash-exp" ;;
                        4) model="gemini/gemini-2.5-pro-exp-03-25" ;;
                        5) model="gemini/gemini-2.5-pro-preview-03-25" ;;
                        0) break ;; # Back to main menu
                        *) echo "Invalid choice. Press Enter to continue..."; read; continue ;; # Continue Google loop
                    esac # END Main model selection case

                    # If architect mode, select editor model
                    if [ "$selected_mode" == "architect" ]; then
                        while true; do
                            display_google_editor_models
                            read editor_choice
                            case $editor_choice in
                                1) selected_editor_model="gemini/gemini-1.5-pro"; break ;;
                                2) selected_editor_model="gemini/gemini-2.0-flash"; break ;;
                                3) selected_editor_model="gemini/gemini-2.0-flash-exp"; break ;;
                                4) selected_editor_model="gemini/gemini-2.5-pro-exp-03-25"; break ;;
                                5) selected_editor_model="gemini/gemini-2.5-pro-preview-03-25"; break ;;
                                9) selected_editor_model="default"; break ;; # Explicitly default
                                0) model=""; break ;; # Go back to selecting main Google model
                                *) echo "Invalid choice. Press Enter to continue..."; read ;;
                            esac
                        done
                        # If user chose 'Back' (model is empty), restart main model selection
                        if [ -z "$model" ]; then continue; fi
                    fi

                    # Launch aider if a model was selected
                    if [ -n "$model" ]; then
                        launch_aider "GOOGLE" "$model" "$selected_mode" "$selected_editor_model"
                        break # Break Google loop after launch
                    fi
                done
                ;;
                
            4) # Update API Keys
                while true; do
                    display_update_api_keys_menu
                    read api_choice
                    
                    case $api_choice in
                        1) update_api_key "OPENAI"; ;;
                        2) update_api_key "ANTHROPIC"; ;;
                        3) update_api_key "GOOGLE"; ;;
                        0) break ;;
                        *) echo "Invalid choice. Press Enter to continue..."; read ;;
                    esac
                    
                    echo "Press Enter to continue..."
                    read
                done
                ;;
                
            0) # Exit
                echo "Goodbye!"
                exit 0
                ;;
                
            *) # Invalid choice
                echo "Invalid choice. Press Enter to continue..."
                read
                ;;
        esac
    done
}

# Run the main function
main
