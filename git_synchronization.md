# Git Synchronization Workflow for Multiple Machines

## Pre-Work Setup
1. **Use a Centralized Repository**
   - Host your project on GitHub, GitLab, or Bitbucket
   - Always treat these remote repositories as the "source of truth"

Let's focus on using GitHub as the primary synchronization method within VSCode:

## Using GitHub in VSCode

1. Before switching laptops:
   - Open the Source Control view in VSCode (Ctrl+Shift+G or Cmd+Shift+G on Mac).
   - Review your changes in the "Changes" section.
   - Stage your changes by clicking the "+" icon next to each file or using the "Stage All Changes" option.
   - Enter a commit message in the text box at the top of the Source Control view.
   - Click the checkmark icon or use Ctrl+Enter (Cmd+Enter on Mac) to commit your changes.
   - Click the "Sync Changes" button in the Source Control view to push your commits to GitHub.

2. When starting work on the other laptop:
   - Open VSCode and ensure you're in the correct repository.
   - In the Source Control view, click on the ellipsis (...) menu and select "Pull" to fetch and merge the latest changes from GitHub[6].
   - Alternatively, you can use the "Sync Changes" button, which will both pull and push changes[6].

## Additional VSCode Features for GitHub Integration

- **GitHub Pull Requests and Issues extension**: This extension allows you to manage workflows, monitor runs, and handle pull requests directly within VSCode[3].

- **Branch management**: Use the branch indicator in the bottom-left corner of VSCode to switch between branches or create new ones[2].

- **Viewing commit history**: Right-click on a file in the explorer and select "View File History" to see all commits related to that file.

- **Resolving conflicts**: If conflicts arise during a pull operation, VSCode provides an inline diff editor to help you resolve them efficiently.

- **GitHub Repositories extension**: For quick edits without cloning, this extension allows you to browse and edit GitHub repositories directly within VSCode.

By leveraging these VSCode features and extensions, you can maintain a smooth workflow between your two MacOS laptops, ensuring that your GitHub repositories stay synchronized and up-to-date.

---

## Recommended Tools
- Use VS Code's built-in Git integration
- Consider GitHub Desktop for visual git management
- Use git-aware shell prompts (like Oh My Zsh) to show branch status

## Best Practices
- Never work directly on the main/master branch
- Create feature branches for development
- Use meaningful, descriptive commit messages
- Commit small, logical chunks of work
- Pull changes frequently
```

## Additional Recommendations
1. Avoid iCloud sync for git repositories
2. Use a dedicated cloud storage or version control system
3. Consider using SSH keys for seamless authentication