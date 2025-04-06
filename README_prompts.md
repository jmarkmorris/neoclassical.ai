# Prompts for Manim

*   Name the scene the same as the filename (or the requested output file) to avoid warnings.
*   Do not add comments specific to a particular problem, issue, or reversion.
*   All comments added should be professional, concise, and explain the overall design or purpose of the code block.

---

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

---

# Aider Conventions Files

Convention files are markdown files that specify coding guidelines for aider to follow. They can include preferences like:

*   Coding style rules
*   Preferred libraries and packages
*   Type hint requirements
*   Testing conventions
*   Documentation standards
*   And more

For more information about using conventions with aider, see the [aider conventions documentation](https://aider.chat/docs/conventions.html).

## How to Use These Conventions

1.  Browse the subdirectories to find a conventions file that matches your needs.
2.  Copy the desired `README_prompts.md` to your project.
3.  Load it in aider using either:
    *   Command line:
        ```bash
        aider --read-only README_prompts.md
        ```
    *   Or add it to your `.aider.conf.yml`:
        ```yaml
        read-only: README_prompts.md
        ```

## Always Load Conventions

You can configure aider to always load your conventions file by adding it to the `.aider.conf.yml` config file:

*   **Single file:**
    ```yaml
    # .aider.conf.yml
    read: README_prompts.md
    ```

*   **Multiple files:**
    ```yaml
    # .aider.conf.yml
    read:
      - README_prompts.md
      - anotherfile.txt
    ```
