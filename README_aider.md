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
