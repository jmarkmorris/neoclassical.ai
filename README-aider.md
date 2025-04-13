# Aider Documentation

## Installing aider

* python -m pip install aider-install
* aider-install

Note: there is also an aider package known to pip, but that is something else.

You can run Aider with the --verbose flag to enable verbose output. This will provide detailed logs and information about the operations being performed. If you are using a configuration file for Aider, you can add the --verbose option to the configuration settings.

## Running Aider with runaider.sh

The `runaider.sh` script provides an interactive command-line interface to configure and launch `aider`. It simplifies the process by:

- Allowing you to choose the operating mode:
    - **Code Mode:** Standard `aider` operation for direct code generation and modification.
    - **Architect Mode:** Uses separate LLMs for high-level planning (Architect) and detailed code implementation (Editor).
- Guiding you through selecting the LLM vendor (OpenAI, Anthropic, Google, Deepseek) and specific model for each role (Code, Architect, Editor).
- Managing API keys securely (loading from environment or files).
- **Allowing pre-launch selection of the Aider edit format** (`whole`/`diff` for Code mode, `editor-whole`/`editor-diff` for Architect mode) via an interactive menu.
- Automatically adding `README-prompts.md` and `README-ask.md` as read-only files to the Aider chat context.

Use `./run-aider.sh` in your terminal to start the configuration process. To see detailed usage instructions, including API key setup and menu flow, run `./run-aider.sh -h` or `./run-aider.sh --help`.

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

Aider's `--edit-format` option controls how code changes are presented to the LLM. The `run-aider.sh` script helps select this format before launching. Understanding the differences can help troubleshoot failed edits.

**`run-aider.sh` Behavior:**

1.  **Initial Defaults:**
    *   **Code Mode:** Initially defaults to the **`whole`** edit format.
    *   **Architect Mode:** Initially defaults to the **`editor-whole`** edit format.
2.  **Pre-Launch Confirmation Menu:** Before executing `aider`, the script shows a menu displaying the currently selected edit format and the full command.
3.  **Switching Formats:** This menu allows pressing '2' to switch to the alternative format:
    *   In Code Mode: Switch between `whole` and `diff`.
    *   In Architect Mode: Switch between `editor-whole` and `editor-diff`.
    The menu updates to show the new format and command before launching.

**Description of Edit Formats:**

1.  **`diff`**
    *   **What it does:** Presents changes in standard `diff` format (`+`/`-` lines).
    *   **How it works:** Sends only calculated differences to the LLM. Aider then attempts to apply this diff/patch to the local file.
    *   **Compatibility:** Primarily for **Code Mode**. Concise, focuses LLM on changes.
    *   **Potential Issues:** Edits can sometimes fail if the LLM generates an invalid diff, if the context lines in the diff don't perfectly match the current file, or if the changes are complex/overlapping.
    *   **`run-aider.sh` Usage:** Selectable via the pre-launch confirmation menu in Code Mode (alternative to `whole`).

2.  **`whole` (Initial Default for Code Mode in script)**
    *   **What it does:** Presents the *entire* proposed file content to the LLM.
    *   **How it works:** Sends the complete intended file text. Aider replaces the existing file content with the new content received from the LLM. This bypasses the complexities of patch application.
    *   **Compatibility:** Works in **Code Mode**. Can be more reliable if `diff` edits fail frequently, as it avoids diff generation/application errors.
    *   **Downsides:** Uses significantly more tokens (higher cost, potentially slower), may hit context limits on very large files, and might encourage the LLM to make broader, unintended changes if not prompted carefully.
    *   **`run-aider.sh` Usage:** The *initial default* in Code Mode. Switchable to `diff` via the pre-launch confirmation menu.

**Architect Mode Specific Formats:**

These control how the *main* LLM's output is presented to the *editor* LLM. The same trade-offs between diff-based and whole-file approaches apply.

3.  **`editor-diff`**
    *   **What it does:** Sends the diff from the *main* LLM's changes to the *editor* LLM.
    *   **How it works:** Editor LLM receives only the diff to review/refine. Aider then attempts to apply the (potentially refined) diff.
    *   **Compatibility:** Only for **Architect Mode**. Focuses editor on refining specific changes.
    *   **Potential Issues:** Subject to the same diff application risks as the standard `diff` format if the main or editor LLM produces a problematic diff.
    *   **`run-aider.sh` Usage:** Selectable via the pre-launch confirmation menu in Architect Mode (alternative to `editor-whole`).

4.  **`editor-whole` (Initial Default for Architect Mode in script)**
    *   **What it does:** Sends the *entire file content* proposed by the *main* LLM to the *editor* LLM.
    *   **How it works:** Editor LLM receives the full proposed file content for review/refinement. Aider then replaces the local file with the final version from the editor LLM. This bypasses diff application issues between the main and editor steps.
    *   **Compatibility:** Only for **Architect Mode**. Gives editor full context; can be more reliable if `editor-diff` fails.
    *   **Downsides:** Uses significantly more tokens than `editor-diff`, potentially increasing cost and latency.
    *   **`run-aider.sh` Usage:** The *initial default* in Architect Mode. Switchable to `editor-diff` via the pre-launch confirmation menu.

**Troubleshooting Edit Failures:**

If you experience frequent failed edits, especially with complex changes, switching from a `diff`-based format (`diff`, `editor-diff`) to a `whole`-based format (`whole`, `editor-whole`) using the `run-aider.sh` pre-launch menu might improve reliability, at the cost of increased token usage.

**Summary:**

*   `run-aider.sh` simplifies selecting Aider's edit format.
*   **Code Mode:** Starts with `whole` (more reliable, higher tokens), allows switching to `diff` (more concise, potential diff issues) before launch.
*   **Architect Mode:** Starts with `editor-whole` (more reliable, higher tokens), allows switching to `editor-diff` (more concise, potential diff issues) before launch.

---

## Changing Aider Settings

You can change aider settings using command line options, a `.aider.conf.yml` file, or environment variables.

*   **Command Line Options:** You can specify settings directly when you run the `aider` command. For example, `aider --dark-mode` enables dark mode.
*   **.aider.conf.yml File:** Create a file named `.aider.conf.yml` in your home directory or at the root of your git repository. You can then add settings to this file in YAML format. For example:

    ```yaml
    dark-mode: true
    ```
*   **Environment Variables:** You can set environment variables to configure aider. The environment variable name is usually `AIDER_` followed by the option name in uppercase. For example, to enable dark mode, you would set `AIDER_DARK_MODE=true`. You can set these variables in your shell or in a `.env` file.

See also:

*   https://aider.chat/docs/config.html
*   https://aider.chat/docs/config/options.html
*   https://aider.chat/docs/faq.html
