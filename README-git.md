# Git Synchronization Workflow for Multiple Machines

## iCloud Tips

   - Use "keep downloaded" for the repo. 
   - Ensure all files are synchronized before launching aider

## Pre-Work Setup

1. **Use a Centralized Repository**

   - Host your project on GitHub, GitLab, or Bitbucket
   - Always treat these remote repositories as the "source of truth"

2. **Global Git Configuration**

   ```bash
   # Set up global git config on both machines
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   
   # Recommended: Set default branch behavior
   git config --global pull.rebase true
   ```

## Workflow Steps

### Before Switching Machines

1. **Always Commit Changes**

   ```bash
   # Stage all changes
   git add .
   
   # Commit with a descriptive message
   git commit -m "Detailed description of changes"
   
   # Push to remote repository
   git push origin [branch-name]
   ```

2. **Pull Latest Changes on New Machine**

   ```bash
   # Navigate to project directory
   cd /path/to/project
   
   # Fetch all remote changes
   git fetch origin
   
   # Pull and rebase current branch
   git pull --rebase origin [branch-name]
   git pull --rebase origin master
   ```

## Conflict Resolution Strategies

**If Conflicts Occur**

   ```bash
   # Identify conflicts
   git status
   
   # Manually resolve conflicts in affected files
   # Open files, look for <<<<<<< HEAD sections
   
   # After resolving, stage resolved files
   git add [conflicted-files]
   
   # Complete the merge/rebase
   git rebase --continue
   ```

## Best Practices

- Never work directly on the main/master branch
- Create feature branches for development
- Use meaningful, descriptive commit messages
- Commit small, logical chunks of work
- Pull changes frequently

## Steps I took to make local neoclassical.ai repo

   ```bash
   cp -r from oldNPQG repo to neoclassical.ai
   rm -rf .git in neoclassical.ai
   git init
   git remote add origin https://github.com/jmarkmorris/neoclassical.ai
   git fetch origin
   git reset --hard origin/master
   ```