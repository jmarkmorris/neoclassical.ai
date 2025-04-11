# Plan: Add Edit Format Switching via Pre-Launch Confirmation

**Goal:** Allow users to easily switch between the `diff`-based and `whole`-based edit formats just before launching Aider, using the script's interactive menu.

**Constraint:** Aider uses a single `--edit-format` flag per run. This plan focuses only on `diff`, `whole`, `editor-diff`, and `editor-whole`.

**Refined Step-by-Step Plan (Based on current `run-aider.sh`):**

1.  **Define Specific Format Constants:**
    *   **Action:** In `run-aider.sh`, replace the existing `ARCHITECT_EDIT_FORMAT` and `CODE_EDIT_FORMAT` constants with four new constants defining the specific format strings for each mode's `diff` and `whole` variants.
    *   **Example:**
        ```bash
        # --- Edit Format Definitions ---
        # Define the specific format strings to use
        CODE_DIFF_FORMAT="diff"
        CODE_WHOLE_FORMAT="whole"
        ARCHITECT_DIFF_FORMAT="editor-diff" # Diff-based format for Architect mode
        ARCHITECT_WHOLE_FORMAT="editor-whole" # Whole-based format for Architect mode

        # Define the INITIAL default format to use when the script starts
        INITIAL_CODE_FORMAT=$CODE_WHOLE_FORMAT # Or $CODE_DIFF_FORMAT
        INITIAL_ARCHITECT_FORMAT=$ARCHITECT_WHOLE_FORMAT # Or $ARCHITECT_DIFF_FORMAT
        ```
        *(Note: The initial defaults above reflect the current state of `run-aider.sh` using `whole`/`editor-whole`. You might choose to start with `diff`/`editor-diff` instead).*
    *   **Goal:** Clearly define all relevant format strings and the starting default.
    *   **Risk:** Very Low.

2.  **Confirm No Intermediate Format Selection:**
    *   **Action:** Verify that no separate format selection function (like `select_format`) or selection steps exist within `run_code_mode` or `run_architect_mode`. (Based on current `run-aider.sh`, this is true).
    *   **Goal:** Ensure selection only happens in the pre-launch menu.
    *   **Risk:** N/A (Verification step).

3.  **Modify `launch_aider` and Helpers (Incorporate Pre-Launch Switching Menu):**
    *   **Action:**
        *   Ensure the `launch_aider` function signature does *not* accept a format choice argument.
        *   **Initial Command Build:**
            *   Inside `launch_aider`, determine the *initial* `actual_format` based on the `mode` argument ("code" or "architect") and the corresponding *initial* default constant (`INITIAL_CODE_FORMAT` or `INITIAL_ARCHITECT_FORMAT`).
            *   Modify `_build_code_args`: Change `echo "--chat-mode code --edit-format ${CODE_EDIT_FORMAT}"` to `echo "--chat-mode code"`.
            *   Modify `_build_architect_args`: Remove the `--edit-format ${ARCHITECT_EDIT_FORMAT}` part from the `args` string construction.
            *   Build the initial `aider_cmd` string by calling the modified helpers and appending the *initial* `--edit-format $actual_format`. Store this command in `current_aider_cmd`.
        *   **Pre-Launch Confirmation Loop:**
            *   Start a `while true` loop.
            *   Inside the loop:
                *   `clear` the screen.
                *   Display the *current* `actual_format` being used.
                *   Display the *current* full command string (`current_aider_cmd`).
                *   Determine the *alternative* format using the constants defined in Step 1:
                    *   If `mode` is "code": if `actual_format` == `$CODE_DIFF_FORMAT`, alternative is `$CODE_WHOLE_FORMAT`; else alternative is `$CODE_DIFF_FORMAT`.
                    *   If `mode` is "architect": if `actual_format` == `$ARCHITECT_DIFF_FORMAT`, alternative is `$ARCHITECT_WHOLE_FORMAT`; else alternative is `$ARCHITECT_DIFF_FORMAT`.
                *   Display the menu, dynamically showing the alternative format:
                    ```
                    ------------------------------
                    Current Edit Format: <actual_format>
                    ------------------------------
                    1. Launch Aider with this command
                    2. Switch to Format: <alternative_format> and Launch
                    3. Back to Main Menu (Abort Launch)
                    ------------------------------
                    Enter choice [1-3, Enter=1]:
                    ```
                *   Read user `confirm_choice`. Default to "1" if empty.
                *   Use a `case` statement on `confirm_choice`:
                    *   `1)`: `break` the loop (proceeds to launch with `current_aider_cmd`).
                    *   `2)`:
                        *   Set `actual_format` to the `alternative_format`.
                        *   **Rebuild `current_aider_cmd`:** Re-call the `_build_main_model_args` and the modified `_build_code_args` or `_build_architect_args` helpers, then append the *new* `--edit-format $actual_format`.
                        *   `break` the loop (proceeds to launch with the *new* `current_aider_cmd`).
                    *   `3)`: `return` from `launch_aider` (goes back to the main script menu).
                    *   `*)`: Invalid choice message, `continue` the loop.
        *   **Execute Command:**
            *   After the loop breaks (only on choice 1 or after choice 2), execute `eval "$current_aider_cmd"`.
            *   Handle exit status as before.
    *   **Goal:** Provide a final confirmation menu that allows a simple toggle between the relevant `diff`-based and `whole`-based formats before execution, using clearly defined constants.
    *   **Risk:** Medium. Modifies `launch_aider` significantly, including command rebuilding logic within the loop. Requires careful modification of helper functions.
