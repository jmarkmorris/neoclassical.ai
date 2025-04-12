# Feature: Edit Format Switching via Pre-Launch Confirmation

**Goal:** Allow users to easily switch between the `diff`-based and `whole`-based edit formats just before launching Aider, using the script's interactive menu.

**Constraint:** Aider uses a single `--edit-format` flag per run. This feature focuses only on `diff`, `whole`, `editor-diff`, and `editor-whole`.

**Implemented Functionality (in `run-aider.sh`):**

1.  **Format Constants Defined:**
    *   The script defines constants for all relevant edit format strings:
        *   `CODE_DIFF_FORMAT="diff"`
        *   `CODE_WHOLE_FORMAT="whole"`
        *   `ARCHITECT_DIFF_FORMAT="editor-diff"`
        *   `ARCHITECT_WHOLE_FORMAT="editor-whole"`
    *   It also defines the *initial* default formats used when the script starts:
        *   `INITIAL_CODE_FORMAT=$CODE_WHOLE_FORMAT` (Defaults to `whole` for Code Mode)
        *   `INITIAL_ARCHITECT_FORMAT=$ARCHITECT_WHOLE_FORMAT` (Defaults to `editor-whole` for Architect Mode)

2.  **Helper Functions Modified:**
    *   The internal helper functions (`_build_code_args`, `_build_architect_args`) no longer hardcode the `--edit-format` flag.

3.  **Pre-Launch Confirmation Menu in `launch_aider`:**
    *   After selecting the mode (Code/Architect) and models, the `launch_aider` function presents a final confirmation menu.
    *   **Displays:**
        *   The selected mode and models.
        *   The *currently selected* edit format (initialized from the `INITIAL_..._FORMAT` constants).
        *   The full `aider` command that will be run with the current format.
    *   **Options:**
        *   **1. Launch Aider:** Executes the displayed command with the current edit format.
        *   **2. Switch Format:** Toggles the edit format to the alternative (e.g., `whole` -> `diff`, `editor-whole` -> `editor-diff`, and vice-versa) and redisplays the menu with the updated format and command.
        *   **3. Back to Main Menu:** Aborts the launch and returns to the script's main mode selection menu.
    *   **Execution:** The `aider` command is executed using `eval` only when option 1 is chosen, ensuring the correct `--edit-format` flag is included based on the final selection in the menu.

**Outcome:** The script provides a user-friendly way to choose between the primary edit format styles (`diff` vs `whole` based) via a pre-launch confirmation menu, starting with configurable defaults.
