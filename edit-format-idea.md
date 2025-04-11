# Plan: Add Edit Format Selection with Pre-Launch Confirmation

**Goal:** Allow users to choose the `--edit-format` used by Aider via the script's interactive menu, with a final confirmation step before launching.

**Constraint:** Aider uses a single `--edit-format` flag per run.

**Revised Step-by-Step Plan:**

1.  **Define Formats and Defaults:**
    *   **Action:** In `run-aider.sh`, define constants for the default edit format for each mode (`DEFAULT_CODE_EDIT_FORMAT`, `DEFAULT_ARCHITECT_EDIT_FORMAT`). Define arrays listing the available format choices for each mode (`CODE_MODE_FORMATS`, `ARCHITECT_MODE_FORMATS`).
    *   **Example:**
        ```bash
        # --- Edit Format Definitions ---
        DEFAULT_CODE_EDIT_FORMAT="diff"
        DEFAULT_ARCHITECT_EDIT_FORMAT="editor-diff" # Default for Architect mode

        # Formats suitable for Code Mode or general main LLM interaction
        CODE_MODE_FORMATS=( "diff" "whole" "udiff" "json" )
        # Formats relevant for Architect Mode (includes editor-specific ones)
        ARCHITECT_MODE_FORMATS=( "diff" "whole" "udiff" "json" "editor-diff" "editor-whole" )
        ```
    *   **Goal:** Centralize format options and defaults.
    *   **Risk:** Very Low.

2.  **Create `select_format` Function:**
    *   **Action:** Create a new function `select_format` in `run-aider.sh`, similar in structure to `select_entity`.
    *   **Arguments:** It should accept the `mode` ("code" or "architect") to determine which list of formats (`CODE_MODE_FORMATS` or `ARCHITECT_MODE_FORMATS`) and which default (`DEFAULT_CODE_EDIT_FORMAT` or `DEFAULT_ARCHITECT_EDIT_FORMAT`) to display in the menu.
    *   **Return:** Use the global variable `SELECT_FORMAT_RESULT` to return the chosen format string (e.g., "diff", "editor-whole") or "default" if the user selects the default option. Handle "Back" (empty string) and invalid input ("invalid") consistently with `select_entity`.
    *   **Goal:** Encapsulate the format selection UI logic.
    *   **Risk:** Low.

3.  **Integrate into `run_code_mode`:**
    *   **Action:**
        *   Add a local variable `selected_format` initialized to "default".
        *   After successfully selecting the model (before `launch_aider`), call `select_format "code"`.
        *   Check the global `SELECT_FORMAT_RESULT`:
            *   If "invalid", loop back to re-call `select_format`.
            *   If empty ("Back"), clear the model selection (`main_model=""`) and loop back to the model selection step.
            *   Otherwise, store the valid result (e.g., "diff", "whole", "default") in `selected_format`.
        *   Modify the call to `launch_aider` to pass `selected_format` as an argument.
    *   **Goal:** Add the format selection step into the Code Mode workflow.
    *   **Risk:** Medium. Modifies UI flow.

4.  **Integrate into `run_architect_mode`:**
    *   **Action:**
        *   Add a local variable `selected_format` initialized to "default".
        *   Add a new state `select_format` to the state machine, placed *after* the editor model selection (`select_editor_model`) is complete (or after `select_editor_vendor` if the vendor choice was "default"), just before the `launch` state.
        *   In the `select_format` state:
            *   Call `select_format "architect"`.
            *   Check `SELECT_FORMAT_RESULT`:
                *   If "invalid", loop back to re-call `select_format`.
                *   If empty ("Back"), transition back to the previous step (`select_editor_model` or `select_editor_vendor` depending on the path taken). Clear the selection made in that previous step (`editor_model=""` or `editor_vendor=""`).
                *   Otherwise, store the valid result in `selected_format` and transition to the `launch` state.
        *   Modify the call to `launch_aider` in the `launch` state to pass `selected_format` as an argument.
    *   **Goal:** Add the format selection step into the Architect Mode workflow.
    *   **Risk:** Medium. Modifies state machine logic.

5.  **Modify `launch_aider` and Helpers (Incorporate Pre-Launch Menu):**
    *   **Action:**
        *   Update the `launch_aider` function signature to accept one new argument for the format choice (e.g., `format_choice`).
        *   **Initial Command Build:**
            *   Inside `launch_aider`, determine the initial `actual_format` based on `format_choice` and `mode` (using defaults if `format_choice` is "default").
            *   Modify `_build_code_args` and `_build_architect_args` to *remove* the `--edit-format` flag from their output.
            *   Build the initial `aider_cmd` string by calling helpers and appending the initial `--edit-format $actual_format`. Store this initial command in a variable (e.g., `current_aider_cmd`).
        *   **Pre-Launch Confirmation Loop:**
            *   Start a `while true` loop.
            *   Inside the loop:
                *   `clear` the screen.
                *   Display the *current* `actual_format`.
                *   Display the *current* full command string (`current_aider_cmd`).
                *   Display the menu:
                    ```
                    ------------------------------
                    1. Launch Aider with this command
                    2. Change Edit Format and Launch
                    3. Back to Main Menu (Abort Launch)
                    ------------------------------
                    Enter choice [1-3, Enter=1]:
                    ```
                *   Read user `confirm_choice`. Default to "1" if empty.
                *   Use a `case` statement on `confirm_choice`:
                    *   `1)`: `break` the loop (proceeds to launch with `current_aider_cmd`).
                    *   `2)`:
                        *   Call `select_format "$mode"`.
                        *   Check `SELECT_FORMAT_RESULT`:
                            *   If "invalid" or empty ("Back"), print a message and `continue` the loop (redisplay confirmation menu with *unchanged* command).
                            *   If a valid format or "default" is returned:
                                *   Update the `format_choice` variable with the new selection.
                                *   Recalculate `actual_format` based on the *new* `format_choice`.
                                *   **Rebuild `current_aider_cmd`:** Re-call the `_build_..._args` helpers and append the *new* `--edit-format $actual_format`.
                                *   `break` the loop (proceeds to launch with the *new* `current_aider_cmd`).
                    *   `3)`: `return` from `launch_aider` (goes back to the main script menu).
                    *   `*)`: Invalid choice message, `continue` the loop.
        *   **Execute Command:**
            *   After the loop breaks (only on choice 1 or after choice 2), execute `eval "$current_aider_cmd"`.
            *   Handle exit status as before.
    *   **Goal:** Provide a final confirmation, allow quick format change, and use the correctly chosen format in the command.
    *   **Risk:** Medium-High. Adds complexity to `launch_aider` with the loop, command rebuilding, and menu logic.
