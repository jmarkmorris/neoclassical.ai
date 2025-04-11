# Plan: Add Edit Format Selection to run-aider.sh

**Goal:** Allow users to choose the `--edit-format` used by Aider via the script's interactive menu.

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

5.  **Modify `launch_aider` and Helpers:**
    *   **Action:**
        *   Update the `launch_aider` function signature to accept one new argument for the format choice (e.g., `format_choice`).
        *   Inside `launch_aider`, determine the *actual* format string to use:
            *   If `format_choice` is "default": use `DEFAULT_CODE_EDIT_FORMAT` if `mode` is "code", or `DEFAULT_ARCHITECT_EDIT_FORMAT` if `mode` is "architect".
            *   Otherwise, use the value of `format_choice`. Store this actual format string in a local variable (e.g., `actual_format`).
        *   Modify `_build_code_args`: Remove the `--edit-format ${CODE_EDIT_FORMAT}` part. The function should now only return `--chat-mode code`.
        *   Modify `_build_architect_args`: Remove the `--edit-format ${ARCHITECT_EDIT_FORMAT}` part. The function should now only return `--architect` and potentially `--editor-model` and editor API key flags.
        *   In `launch_aider`, append the final edit format flag to the `aider_cmd` string *after* calling the helper functions: `aider_cmd="$aider_cmd --edit-format $actual_format"`.
        *   Update the status message printed before execution (e.g., `echo "Launching aider in ... with format: $actual_format..."`) to show the chosen/default format being used.
    *   **Goal:** Ensure the single, correctly chosen edit format is used in the final `aider` command execution.
    *   **Risk:** Medium. Changes command construction logic across multiple functions.
