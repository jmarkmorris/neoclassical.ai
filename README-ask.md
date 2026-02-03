# This is a collection of prompts for asking aider questions about the current codebase.

# --- General Review & Planning ---

/ask Review the current code. Identify potential areas for improvement (e.g., readability, performance, error handling, security). Propose a step-by-step plan for implementing these changes, ordered by least risk.

/ask Analyze the code for adherence to the principles outlined in README-prompts.md (readability, simplicity, meaningful names, small functions, etc.). Suggest specific refactorings to improve compliance and provide a safe, incremental plan.

/ask Review the code specifically for opportunities to improve robustness and error handling. Identify areas where exceptions could be handled better or where edge cases might not be covered. Propose changes with a step-by-step plan.

/ask Examine the code for redundancy (DRY principle violations). Suggest ways to consolidate duplicated logic or data. Provide a step-by-step refactoring plan.

/ask Review the code for adherence to popular conventions and the style guide in README-prompts.md (import order, type hinting, docstrings, constants, formatting). Ensure all constants and tunable parameters are defined appropriately (e.g., at the module level). Create a plan to apply these changes incrementally.

/ask Don't write code for this prompt. While it's ok to consider how this code will be written and used, the goal is for your output to be a set of design decisions that can be passed to the editor, such that the editor can then write the markdown file for you. Therefore focus on the documenting your design decisions. Avoid code snippets unless they provide drastic improvements in design clarity, and in that case keep them highly concise so they articulate the design decision by example.

# --- Specific Tasks ---

/ask Identify any functions or modules that seem overly complex or long. Suggest how they could be broken down into smaller, more manageable units. Provide a refactoring plan.

/ask Review the existing comments and docstrings. Are they accurate, clear, and necessary? Suggest improvements or additions, focusing on explaining the 'why' rather than the 'what'.

/ask Look for potential performance bottlenecks in the code. Suggest optimizations and provide a plan to implement and test them.

/ask Analyze the code for potential security vulnerabilities (e.g., injection risks, improper handling of sensitive data). Suggest fixes and provide an implementation plan.

/ask Suggest areas where unit tests or integration tests could be added or improved to increase code coverage and reliability. Outline a plan for writing these tests.

/ask Refactor the function `[function_name]` (or class `[class_name]`) to improve its [readability|performance|robustness]. Provide a step-by-step plan.

/ask Ensure all public functions and classes have comprehensive docstrings following the format specified in README-prompts.md. Create a plan to add or update them.
