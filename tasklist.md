# run-aider.sh Refactoring Tasks

Based on the analysis using `README_ask.md` and `README_prompts.md`, here are potential refactoring tasks for `run-aider.sh`, ordered by approximate risk/benefit:

1.  **Refactor `select_entity` Return Value:**
    *   **Action:** Modify `select_entity` to print its result (selected entity, "invalid", "default", or empty string for back) to standard output instead of using the global `SELECT_ENTITY_RESULT`. Update the calling functions (`run_code_mode`, `run_architect_mode`) to capture this output using command substitution (e.g., `selection_result=$(select_entity ...)`).
    *   **Goal:** Improve data flow clarity, reduce reliance on global variables, adhere closer to functional principles.
    *   **Risk:** Low-Medium. Requires careful changes in `select_entity` and its call sites.

3.  **Refactor `load_api_keys`:**
    *   **Action:** Break down the function into smaller, more focused units (e.g., `_load_keys_from_env`, `_find_keys_file`, `_load_keys_from_file`). The main `load_api_keys` function would orchestrate calls to these helpers.
    *   **Goal:** Improve readability, testability, and maintainability by reducing the size and complexity of the main loading function.
    *   **Risk:** Medium. Changes core initialization logic; requires careful management of variable scope and return values between helper functions.

4.  **Simplify `run_architect_mode` State Machine (Optional/Low Priority):**
    *   **Action:** Analyze if the explicit `current_step` variable is necessary or if the flow can be managed with nested loops or conditional checks in a more linear fashion while maintaining clarity.
    *   **Goal:** Potentially improve readability if a simpler structure is found.
    *   **Risk:** Medium. Could simplify or complicate readability depending on the alternative implementation. Current state machine is functional and relatively clear.
