# Coding Environment

*   The development environment operating system is MacOS. Microsoft Windows is not used in the development environment. All keystroke sequences should be for MacOS.
*   iterm2 is the main terminal interface.
*   The shell is bash. If I ask you to work on a shell script please remind me that I strongly prefer python.
*   The run-aider.sh script that enables choice of LLM models and aider command line options.

# General Coding Principles

When writing code, you MUST follow these principles:

*   **Readability:** Code should be easy to read and understand.
*   **Simplicity:** Keep the code as simple as possible. Avoid unnecessary complexity.
*   **Meaningful Names:** Use meaningful names for variables, functions, classes, etc. Names should reveal intent.
*   **Small Functions:** Functions should be small and do one thing well. Aim for functions not exceeding a few logical lines.
*   **Descriptive Function Names:** Function names should clearly describe the action being performed.
*   **Limited Arguments:** Prefer fewer arguments in functions. Ideally, aim for no more than two or three.
*   **Self-Explanatory Code:** Strive to make the code self-explanatory, reducing the need for comments.
*   **Useful Comments:** Only use comments when necessary. When used, they should add useful information not readily apparent from the code itself (e.g., explaining *why* something is done a certain way, not *what* it does).
*   **Robustness:** Properly handle errors and exceptions to ensure the software's robustness. Use exceptions rather than error codes.
*   **Security:** Consider security implications. Implement security best practices to protect against vulnerabilities and attacks.
*   **Functional Programming Principles:** Adhere to these principles where applicable:
    *   Pure Functions
    *   Immutability
    *   Function Composition
    *   Declarative Code

# Coding Standards & Style

*   **Import Order:** Group imports: 1. Standard library, 2. Third-party packages, 3. Local application/library imports. Alphabetize within each group.
*   **Type Hinting:** Use type hints for all function signatures. Encouraged for complex variable assignments.
*   **Docstrings:** Use well written docstrings for all public classes and functions. Include `Args`, `Returns`, and `Raises` sections where applicable.
*   **Constants:** Define constants at the module level using `UPPER_SNAKE_CASE`.
*   **Formatting:** Code should adhere to Black formatting standards. Run `black .` before committing.

# Design & Architecture

*   **Configuration Management:** Prefer loading configuration from YAML files or using environment variables over hardcoding.
*   **Error Handling Specifics:** Define custom exception classes inheriting from a base application exception where appropriate for distinct error conditions.

# AI Prompts, Interaction, & Workflow

*   **Ask Clarifying Questions:** If a request is unclear or ambiguous, please ask for clarification before proceeding.
*   **Explain Rationale:** For non-trivial changes, briefly explain the 'why' behind the chosen approach, not just the 'what'.
*   **Suggest Alternatives:** Feel free to suggest alternative implementations if you believe they offer significant advantages (e.g., performance, readability, simplicity).
*   **Handling Large Requests:** If a request involves extensive changes, propose a plan or ask for the request to be broken down into smaller, manageable steps.
*   Always provide feedback to each prompt, regarding how to express the prompt request concisely!
*   Comments should explain the overall design and purpose of the code block.
*   All comments added should be professional and concise.
*   Comments should not be parochial, i.e., specific to a particular problem, issue, or revision.
*   Ensure the editor makes small incremental search/replace blocks and keep the changes that succeed.
*   Explicitly verify that *all* requested changes within the prompt have been successfully applied to the relevant files. 

