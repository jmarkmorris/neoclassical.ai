# run-aider.sh Refactoring Tasks

Based on the analysis using `README_ask.md` and `README_prompts.md`, here are potential refactoring tasks for `run-aider.sh`, ordered by approximate risk/benefit:

1.  **Refactor `select_entity` Return Value:**
    *   **Action:** Modify `select_entity` to print its result (selected entity, "invalid", "default", or empty string for back) to standard output instead of using the global `SELECT_ENTITY_RESULT`. Update the calling functions (`run_code_mode`, `run_architect_mode`) to capture this output using command substitution (e.g., `selection_result=$(select_entity ...)`).
    *   **Goal:** Improve data flow clarity, reduce reliance on global variables, adhere closer to functional principles.
    *   **Risk:** Low-Medium. Requires careful changes in `select_entity` and its call sites.

2.  **Simplify `run_architect_mode` State Machine (Optional/Low Priority):**
    *   **Action:** Analyze if the explicit `current_step` variable is necessary or if the flow can be managed with nested loops or conditional checks in a more linear fashion while maintaining clarity.
    *   **Goal:** Potentially improve readability if a simpler structure is found.
    *   **Risk:** Medium. Could simplify or complicate readability depending on the alternative implementation. Current state machine is functional and relatively clear.
