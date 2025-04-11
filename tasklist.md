# run-aider.sh Refactoring Tasks

Based on the analysis using `README_ask.md` and `README_prompts.md`, here are the remaining refactoring tasks for `run-aider.sh`, ordered by approximate risk/complexity:

1.  **Refactor `load_api_keys`:**
    *   **Action:** Break down the function into smaller, more focused units (e.g., one for env vars, one for finding/loading from files).
    *   **Goal:** Improve readability and testability.
    *   **Risk:** Medium. Changes core initialization logic.

2.  **Refactor `eval` in `launch_aider`:**
    *   **Action:** Instead of building `$aider_cmd` as a single string, build the command and its arguments into a bash array (e.g., `local cmd_array=("aider" "--vim" ...)`). Execute using `"${cmd_array[@]}"`.
    *   **Goal:** Improve security posture and robustness (handles spaces/quoting better).
    *   **Risk:** Medium. Changes how the final command is executed.

3.  **Simplify `run_architect_mode` State Machine (Optional):**
    *   **Action:** Analyze if the explicit `current_step` variable is necessary or if the flow can be managed with nested loops or conditional checks in a more linear fashion.
    *   **Goal:** Potentially improve readability.
    *   **Risk:** Medium-High. Could simplify or complicate readability depending on the implementation.

4.  **Parallel Arrays (Optional):**
    *   **Action:** For improved readability (if bash version allows, typically 4.0+), consider using associative arrays for mapping vendors to their key flags and sources (`VENDORS`, `VENDOR_API_KEY_FLAGS`, `VENDOR_KEY_SOURCE`).
    *   **Goal:** Improve readability.
    *   **Risk:** Low (if bash version compatible), but reduces portability to older bash versions.
