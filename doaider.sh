#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

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
    
    echo -e "${YELLOW}Please enter your $vendor API key:${NC}"
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
    
    echo -e "${GREEN}API key updated successfully!${NC}"
}

# Function to display the main menu
display_main_menu() {
    clear
    echo -e "${BLUE}==============================${NC}"
    echo -e "${BLUE}    LLM VENDOR SELECTION     ${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo "1. OpenAI"
    echo "2. Anthropic"
    echo "3. Google"
    echo "4. Update API Keys"
    echo "0. Exit"
    echo -e "${BLUE}==============================${NC}"
    echo -n "Enter your choice [0-4]: "
}

# Function to display OpenAI models
display_openai_models() {
    clear
    echo -e "${BLUE}==============================${NC}"
    echo -e "${BLUE}      OpenAI MODELS          ${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo "1. gpt-4o"
    echo "2. gpt-4o-mini"
    echo "3. gpt-4-turbo"
    echo "4. gpt-4"
    echo "5. gpt-3.5-turbo"
    echo "0. Back to main menu"
    echo -e "${BLUE}==============================${NC}"
    echo -n "Enter your choice [0-5]: "
}

# Function to display Anthropic models
display_anthropic_models() {
    clear
    echo -e "${BLUE}==============================${NC}"
    echo -e "${BLUE}      ANTHROPIC MODELS       ${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo "1. claude-3-7-sonnet-20250219"
    echo "2. claude-3-5-sonnet-20240620"
    echo "3. claude-3-opus-20240229"
    echo "4. claude-3-5-haiku-20240307"
    echo "5. claude-3-sonnet-20240229"
    echo "6. claude-3-haiku-20240307"
    echo "0. Back to main menu"
    echo -e "${BLUE}==============================${NC}"
    echo -n "Enter your choice [0-6]: "
}

# Function to display Google models
display_google_models() {
    clear
    echo -e "${BLUE}==============================${NC}"
    echo -e "${BLUE}       GOOGLE MODELS         ${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo "1. gemini/gemini-1.5-pro"
    echo "2. gemini/gemini-2.0-flash"
    echo "3. gemini/gemini-2.0-flash-exp"
    echo "4. gemini/gemini-2.5-pro-exp-03-25"
    echo "0. Back to main menu"
    echo -e "${BLUE}==============================${NC}"
    echo -n "Enter your choice [0-4]: "
}

# Function to update API keys menu
display_update_api_keys_menu() {
    clear
    echo -e "${BLUE}==============================${NC}"
    echo -e "${BLUE}      UPDATE API KEYS        ${NC}"
    echo -e "${BLUE}==============================${NC}"
    echo "1. OpenAI API Key"
    echo "2. Anthropic API Key"
    echo "3. Google API Key"
    echo "0. Back to main menu"
    echo -e "${BLUE}==============================${NC}"
    echo -n "Enter your choice [0-3]: "
}

# Function to launch aider with the selected model
launch_aider() {
    local vendor=$1
    local model=$2
    local api_key_var="${vendor}_API_KEY"
    local api_key=$(eval echo \$$api_key_var)

    # Check if API key is set
    if [ -z "$api_key" ]; then
        echo -e "${YELLOW}API key for $vendor is not set. Let's update it.${NC}"
        update_api_key $vendor
        api_key=$(eval echo \$$api_key_var)
    fi

    # Prepare aider command based on vendor
    case $vendor in
        OPENAI)
            export OPENAI_API_KEY="$api_key"
            aider_cmd="aider --openai-api-key $api_key --model $model"
            ;;
        ANTHROPIC)
            export ANTHROPIC_API_KEY="$api_key"
            aider_cmd="aider --anthropic-api-key $api_key --model $model"
            ;;
        GOOGLE)
            export GOOGLE_API_KEY="$api_key"
            aider_cmd="aider --api-key google=$api_key --model $model"
            ;;
        *)
            echo "Unknown vendor: $vendor"
            return 1
            ;;
    esac

    # Check if aider is installed
    if ! command -v aider &> /dev/null; then
        echo -e "${YELLOW}Aider is not installed. Please install it first with:${NC}"
        echo "pip install aider-chat"
        read -p "Press Enter to continue..."
        return 1
    fi

    # Launch aider
    echo -e "${GREEN}Launching aider with $model...${NC}"
    echo "Command: $aider_cmd"
    echo
    eval $aider_cmd
}

# Main function
main() {
    load_api_keys
    
    while true; do
        display_main_menu
        read choice
        
        case $choice in
            1) # OpenAI
                while true; do
                    display_openai_models
                    read model_choice
                    
                    case $model_choice in
                        1) launch_aider "OPENAI" "gpt-4o"; break ;;
                        2) launch_aider "OPENAI" "gpt-4o-mini"; break ;;
                        3) launch_aider "OPENAI" "gpt-4-turbo"; break ;;
                        4) launch_aider "OPENAI" "gpt-4"; break ;;
                        5) launch_aider "OPENAI" "gpt-3.5-turbo"; break ;;
                        0) break ;;
                        *) echo "Invalid choice. Press Enter to continue..."; read ;;
                    esac
                done
                ;;
                
            2) # Anthropic
                while true; do
                    display_anthropic_models
                    read model_choice
                    
                    case $model_choice in
                        1) launch_aider "ANTHROPIC" "claude-3-7-sonnet-20250219"; break ;;
                        2) launch_aider "ANTHROPIC" "claude-3-5-sonnet-20240620"; break ;;
                        3) launch_aider "ANTHROPIC" "claude-3-opus-20240229"; break ;;
                        4) launch_aider "ANTHROPIC" "claude-3-5-haiku-20240307"; break ;;
                        5) launch_aider "ANTHROPIC" "claude-3-sonnet-20240229"; break ;;
                        6) launch_aider "ANTHROPIC" "claude-3-haiku-20240307"; break ;;
                        0) break ;;
                        *) echo "Invalid choice. Press Enter to continue..."; read ;;
                    esac
                done
                ;;
                
            3) # Google
                while true; do
                    display_google_models
                    read model_choice
                    
                    case $model_choice in
                        1) launch_aider "GOOGLE" "gemini-1.5-pro"; break ;;
                        2) launch_aider "GOOGLE" "gemini-1.5-flash"; break ;;
                        3) launch_aider "GOOGLE" "gemini-2.0-flash"; break ;;
                        4) launch_aider "GOOGLE" "gemini-2.5-pro-experimental"; break ;;
                        0) break ;;
                        *) echo "Invalid choice. Press Enter to continue..."; read ;;
                    esac
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
