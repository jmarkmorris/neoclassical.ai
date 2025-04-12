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
- Guiding you through selecting the LLM vendor (OpenAI, Anthropic, Google, Deepseek) and specific model for each role (Code, Architect, Editor).
- Managing API keys securely (loading from environment or files).
- **Allowing pre-launch selection of the Aider edit format** (`whole`/`diff` for Code mode, `editor-whole`/`editor-diff` for Architect mode).
- Automatically adding `README_prompts.md` and `README_ask.md` as read-only files to the Aider chat context.

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

Run aider with the `--vim` switch (automatically included by `run-aider.sh`) to enable vi/vim keybindings:

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

## Edit Formats (`--edit-format`) and `run-aider.sh`

Aider's `--edit-format` option controls how code changes are presented *to the LLM* for review and modification. The `run-aider.sh` script provides a convenient way to select the desired format just before launching.

**`run-aider.sh` Behavior:**

1.  **Initial Defaults:**
    *   When you select **Code Mode**, the script initially defaults to the **`whole`** edit format (`INITIAL_CODE_FORMAT=$CODE_WHOLE_FORMAT`).
    *   When you select **Architect Mode**, the script initially defaults to the **`editor-whole`** edit format (`INITIAL_ARCHITECT_FORMAT=$ARCHITECT_WHOLE_FORMAT`).
2.  **Pre-Launch Menu:** Before executing `aider`, the script shows a confirmation menu displaying the currently selected edit format and the full command.
3.  **Switching Formats:** This menu allows you to press '2' to switch to the alternative format:
    *   In Code Mode: Switch between `whole` and `diff`.
    *   In Architect Mode: Switch between `editor-whole` and `editor-diff`.
    The menu will update to show the newly selected format and the corresponding command before you launch.

**Description of Edit Formats:**

1.  **`diff`**
    *   **What it does:** Presents proposed changes in a standard `diff` format (lines starting with `+` or `-`).
    *   **How it works:** Sends only the calculated differences to the LLM.
    *   **Compatibility:** Primarily used for **Code Mode**. Concise, focuses the LLM on changes.
    *   **`run-aider.sh` Usage:** Available via the pre-launch menu in Code Mode (alternative to the default `whole`).

2.  **`whole` (Initial Default for Code Mode in script)**
    *   **What it does:** Presents the *entire* proposed content of the file to the LLM.
    *   **How it works:** Sends the complete file text the LLM intends to write.
    *   **Compatibility:** Works in **Code Mode**. Useful if diffs are confusing the LLM, but uses more tokens.
    *   **`run-aider.sh` Usage:** The *initial default* when selecting Code Mode. Can be switched to `diff` via the pre-launch menu.

3.  **`udiff`**
    *   **What it does:** Uses the "unified" diff format (like `git diff -U`).
    *   **How it works:** Calculates and presents changes using the unified diff standard.
    *   **Compatibility:** Works in **Code Mode**.
    *   **`run-aider.sh` Usage:** Not directly selectable via the script's menu.

**Architect Mode Specific Formats:**

These control how the *main* LLM's output is presented to the *editor* LLM.

4.  **`editor-diff`**
    *   **What it does:** Sends the diff calculated from the *main* LLM's proposed changes to the *editor* LLM.
    *   **How it works:** Editor LLM receives only the diff to review/refine.
    *   **Compatibility:** Only relevant in **Architect Mode**. Focuses the editor on refining specific changes.
    *   **`run-aider.sh` Usage:** Available via the pre-launch menu in Architect Mode (alternative to the default `editor-whole`).

5.  **`editor-whole` (Initial Default for Architect Mode in script)**
    *   **What it does:** Sends the *entire file content* proposed by the *main* LLM to the *editor* LLM.
    *   **How it works:** Editor LLM receives the full proposed file content.
    *   **Compatibility:** Only relevant in **Architect Mode**. Gives editor full context, but uses more tokens.
    *   **`run-aider.sh` Usage:** The *initial default* when selecting Architect Mode. Can be switched to `editor-diff` via the pre-launch menu.

**Summary:**

*   `run-aider.sh` simplifies selecting edit formats.
*   **Code Mode:** Starts with `whole`, allows switching to `diff` before launch.
*   **Architect Mode:** Starts with `editor-whole`, allows switching to `editor-diff` before launch.
