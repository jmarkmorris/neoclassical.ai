# run-aider.sh Refactoring Tasks

Based on the analysis using `README_ask.md` and `README_prompts.md`, here are potential refactoring tasks for `run-aider.sh`, ordered by approximate risk/benefit:

1.  **Refactor `select_entity` Return Value:**
    *   **Action:** Modify `select_entity` to print its result (selected entity, "invalid", "default", or empty string for back) to standard output instead of using the global `SELECT_ENTITY_RESULT`. Update the calling functions (`run_code_mode`, `run_architect_mode`) to capture this output using command substitution (e.g., `selection_result=$(select_entity ...)`).
    *   **Goal:** Improve data flow clarity, reduce reliance on global variables, adhere closer to functional principles.
    *   **Risk:** Low-Medium. Requires careful changes in `select_entity` and its call sites.

2.  **Add More High-Level Comments:**
    *   **Action:** Add comments explaining the overall purpose and flow of major sections like API key loading, mode selection loops, and command construction.
    *   **Goal:** Improve overall understanding for future maintenance.
    *   **Risk:** Very Low.

3.  **Improve Portability/Robustness:**
    *   **Action:** Ensure `local` is used for *all* function-scoped variables unless explicitly global. Review use of bash-specific features like `mapfile` (consider `while read` for max portability) and `[[ ]]`. Ensure consistent use of `printf` over `echo` for potentially problematic strings.
    *   **Goal:** Increase robustness and potentially widen compatibility.
    *   **Risk:** Low.

4.  **Refactor `launch_aider`:**
    *   **Action:** Break down the `launch_aider` function. Extract the pre-launch confirmation menu and logic into a separate helper function. This helper could take the base command array and current format as input and return the final command array to execute or an indication to abort.
    *   **Goal:** Improve readability and maintainability by reducing the size and complexity of `launch_aider`, adhering to the "Small Functions" principle.
    *   **Risk:** Low-Medium. Primarily involves moving code and adjusting function calls/return values.

5.  **Consolidate Argument Building Logic:**
    *   **Action:** Analyze `_build_main_model_args` and `_build_architect_args`. Identify common logic (like handling the API key flag based on source) and extract it into a shared helper function.
    *   **Goal:** Reduce code duplication (DRY principle).
    *   **Risk:** Low-Medium. Requires careful extraction and parameterization of the shared logic.

6.  **Simplify `select_entity`:**
    *   **Action:** Consider splitting `select_entity` into `select_vendor` and `select_model` functions. The special "default" logic for the editor vendor could be handled within the `run_architect_mode` flow.
    *   **Goal:** Reduce the complexity of `select_entity`, improve clarity.
    *   **Risk:** Medium. Requires significant restructuring of the selection logic in `run_code_mode` and `run_architect_mode`.

7.  **Refactor API Key Handling:**
    *   **Action:** Modify `load_api_keys` and its helpers (`_load_keys_from_env`, `_load_keys_from_file`) to avoid modifying the global `VENDOR_KEY_SOURCE` array directly. Instead, have `load_api_keys` return information about key sources (perhaps an associative array or structured string) or have `check_api_key` determine the source when needed. Modify `_build_main_model_args` and `_build_architect_args` to use this returned information instead of the global array.
    *   **Goal:** Further reduce global state, improve data encapsulation, make key source logic more self-contained.
    *   **Risk:** Medium. Affects several core functions related to API key management and command building. Requires careful handling of return values (associative arrays can be tricky in bash for compatibility).


