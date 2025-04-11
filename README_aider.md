# Aider Documentation

## Installling aider

* python -m pip install aider-install
* aider-install

Note: there is also an aider package known to pip, but that is something else.

You can run Aider with the --verbose flag to enable verbose output. This will provide detailed logs and information about the operations being performed.
If you are using a configuration file for Aider, you can add the --verbose option to the configuration settings.

## Running Aider with runaider.sh

The `runaider.sh` script provides an interactive command-line interface to configure and launch `aider`. It simplifies the process by:

- Allowing you to choose the operating mode:
    - **Code Mode:** Standard `aider` operation for direct code generation and modification.
    - **Architect Mode:** Uses separate LLMs for high-level planning (Architect) and detailed code implementation (Editor).
- Guiding you through selecting the LLM vendor (OpenAI, Anthropic, Google) and specific model for each role (Code, Architect, Editor).
- Managing API keys securely.
- Automatic /add of files in read-only mode. See this line: 
- local aider_cmd="aider --vim --no-auto-commit --read README_prompts.md --read README_ask.md"

Use `./runaider.sh` in your terminal to start the configuration process.

---

## Documentation and References

LLMs know about standard tools and libraries but may have outdated information about API versions and function arguments. You can provide up-to-date documentation by:

- Pasting doc snippets directly into the chat
- Including a URL to docs in your chat message for automatic scraping (example: `Add a submit button like this https://ui.shadcn.com/docs/components/button`)
- Using the `/read` command to import doc files from your filesystem

## Creating New Files

To create a new file:
1. Add it to the repository first with `/add <file>`
2. This ensures aider knows the file exists and will write to it
3. Without this step, aider might modify existing files even when you request a new one

## Sending Multi-line Messages

Multiple options for sending long, multi-line messages:

- Enter `{` alone on the first line to start a multiline message and `}` alone on the last line to end it
- Use `{tag` to start and `tag}` to end (useful when your message contains closing braces)
- Use `/paste` to insert text from clipboard directly into the chat

## Vi/Vim Keybindings

Run aider with the `--vim` switch to enable vi/vim keybindings:

| Key | Function |
|-----|----------|
| Up Arrow | Move up one line in current message |
| Down Arrow | Move down one line in current message |
| Ctrl-Up | Scroll back through previous messages |
| Ctrl-Down | Scroll forward through previous messages |
| Esc | Switch to command mode |
| i | Switch to insert mode |
| a | Move cursor right and switch to insert mode |
| A | Move to end of line and switch to insert mode |
| I | Move to beginning of line and switch to insert mode |
| h | Move cursor left |
| j | Move cursor down |
| k | Move cursor up |
| l | Move cursor right |
| w | Move forward one word |
| b | Move backward one word |
| 0 | Move to beginning of line |
| $ | Move to end of line |
| x | Delete character under cursor |
| dd | Delete current line |
| u | Undo last change |
| Ctrl-R | Redo last undone change |

## Tips

- /paste : pastes image from clipboard
- /web : goes to url and scrapes it.
- /clear : erases context other than the files.

---

## Edit Formats (`--edit-format`)

Aider's `--edit-format` option controls how code changes are presented *to the LLM* for review and modification. These aren't separate "editor modes" like the script's `code` vs `architect` modes, but rather configuration *within* those modes.

Here are the main edit formats and their applicability:

1.  **`diff` (Default for Code Mode)**
    *   **What it does:** Presents the proposed code changes to the LLM in a standard `diff` or patch format (similar to `git diff`). It shows lines to be added (prefixed with `+`) and lines to be removed (prefixed with `-`), along with some surrounding context lines.
    *   **How it works:** Aider calculates the difference between the current file state and the LLM's proposed new state and sends only this difference back to the LLM in the next turn (or when asking the LLM to apply changes).
    *   **Compatibility:** Primarily used and the default for **Code Mode**. It's concise and focuses the LLM on the specific changes. It *can* technically be used in Architect mode for the *main* LLM, but the `editor-*` formats are usually preferred for the *editor* LLM in that mode.
    *   **`run-aider.sh` Usage:** This is the format set by `CODE_EDIT_FORMAT="diff"` and used when you select "Code Mode".

2.  **`whole`**
    *   **What it does:** Presents the *entire* proposed content of the file to the LLM, not just the differences.
    *   **How it works:** Instead of calculating a diff, Aider sends the complete text that the file *should* contain according to the LLM's proposal.
    *   **Compatibility:** Works in **Code Mode**. It can be useful if the LLM gets confused by complex diffs or needs to see the full context of the file to make accurate changes. However, it uses more tokens.
    *   **`run-aider.sh` Usage:** Not currently used by the script.

3.  **`udiff`**
    *   **What it does:** Similar to `diff`, but uses the "unified" diff format (like `git diff -U`). It often includes slightly more context lines than the default `diff`.
    *   **How it works:** Calculates and presents changes using the unified diff standard.
    *   **Compatibility:** Works in **Code Mode**. It's an alternative to `diff` if you prefer that specific format.
    *   **`run-aider.sh` Usage:** Not currently used by the script.

**Architect Mode Specific Formats:**

These formats control how the *main* LLM's proposed changes are presented to the *secondary (editor)* LLM in Architect mode.

4.  **`editor-diff` (Default for Architect Mode in the script)**
    *   **What it does:** Takes the diff generated by the *main* LLM and sends *that diff* to the *editor* LLM for review and potential refinement.
    *   **How it works:** The main LLM produces a change (conceptually). Aider calculates the diff for this change. This diff is then passed as input to the editor LLM.
    *   **Compatibility:** Only relevant and used in **Architect Mode**. It allows the editor LLM to focus specifically on refining the *changes* proposed by the main LLM.
    *   **`run-aider.sh` Usage:** This is the format set by `ARCHITECT_EDIT_FORMAT="editor-diff"` and used when you select "Architect Mode".

5.  **`editor-whole`**
    *   **What it does:** Takes the *entire file content* as proposed by the *main* LLM and sends it to the *editor* LLM.
    *   **How it works:** The main LLM produces a complete proposed file. This entire file content is passed as input to the editor LLM.
    *   **Compatibility:** Only relevant and used in **Architect Mode**. This gives the editor LLM the full context of the proposed file, which might be useful for broader consistency checks but uses more tokens.
    *   **`run-aider.sh` Usage:** Not currently used by the script.

**Summary:**

*   **Code Mode:** Typically uses `diff` (default), `whole`, or `udiff` to format changes for the *single* LLM being used. The script uses `diff`.
*   **Architect Mode:** Uses *two* LLMs.
    *   The `--edit-format` flag (like `diff`, `whole`) controls how changes are presented to the *main* LLM.
    *   The `--edit-format` flag set to `editor-diff` or `editor-whole` controls how the main LLM's output is presented to the *editor* LLM. The script uses `editor-diff` for this interaction.


