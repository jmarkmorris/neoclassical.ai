# Virtual Environment Setup Guide

This guide provides instructions on setting up and using Python virtual environments.

## What is a Virtual Environment?

A virtual environment is a self-contained directory that holds a specific Python interpreter and any packages installed for a particular project. This isolates project dependencies, preventing conflicts between different projects that might require different versions of the same packages.

## Why Use Virtual Environments?

- **Isolation:** Each project has its own dependencies, avoiding conflicts.
- **Dependency Management:** Easily manage and track project dependencies.
- **Reproducibility:** Ensure consistent environments across different machines.

## Basic Commands

Here's a quick reference to common virtual environment commands:

- **Create:** `python3 -m venv myenv`
- **Activate:** `source myenv/bin/activate`
- **Install:** `pip install package_name`
- **List Packages:** `pip list` or `pip freeze`
- **Freeze Dependencies:** `pip freeze > requirements.txt`
- **Deactivate:** `deactivate`
- **Delete:** `rm -rf myenv`

## Step-by-Step Instructions

### Step 1: Create the Virtual Environment

Use the following command to create a new virtual environment:

```bash
    python3 -m venv myenv
```

#### Important Notes:

- We use `python3` because macOS (as of Ventura) ships with Python 2.7 😱 as `python`.
- `python3` is the one you installed separately (hopefully via brew install python 🙏).
- If you just installed Python 3.x via Homebrew, `python3` is the correct command.
- `venv` is a module (`-m` means "treat this as a module, not an executable").

#### Naming your Virtual Environment

- `myenv` is just the name (directory) of your virtual environment. Choose a name that makes sense for your project. Some common conventions include:
- `venv` (classic, but confusing if you have many projects)
- `.venv` (dot makes it hidden by default — I like this, keeps dirs clean)
- `any-name-you-choose`

Just don't name it `venv` inside your actual project directory in VSCode because it'll get confused 🤪.

This command will silently create a directory `myenv` (or whatever you named it) containing:

```
myenv/
├── bin          # <-- this is where the magic happens
│   ├── activate
│   ├── pip
│   ├── pip3
│   ├── python -> python3.13 (or whatever version you have)
│   └── python3 -> python3.13 (symlinks, rejoice!)
├── include
├── lib          # <-- all your packages will live here (site-packages inside)
│   └── python3.13
│       └── site-packages
└── pyvenv.cfg   # <-- config file saying "hey, this is Python 3.13, home is /usr/local/bin/python3.13" etc
```

### Step 2: Activate the Virtual Environment

This is the most important step. Until you do this, you're still using the system Python (or the one your shell found first in `$PATH`). To "enter" your isolated world:

```bash
    source myenv/bin/activate
```

(Note: `source` is a shell built-in meaning "read and execute commands from this file in the current shell". Don't confuse with just running `myenv/bin/activate` which wouldn't work because it needs to modify the current shell's environment.)

As soon as you hit Enter, you'll see your command prompt changing:

```
user@macbook ~/Projects/MyAwesomeDjangoProject $
(myenv) user@macbook ~/Projects/MyAwesomeDjangoProject $
```

That `(myenv)` prefix means you're IN. Now:

- `python` will point to `myenv/bin/python` (not `/usr/bin/python` or `/usr/local/bin/python3`)
- `pip` will install packages inside `myenv/lib/python3.x/site-packages/`
- Any python you run will use those packages, not the global ones.

### Step 3: Working Inside the Virtual Environment

#### Install Packages

Just use `pip` as usual. Example:

```bash
    pip install requests django==4.0.1 numpy pandas
```

All packages will be installed into `myenv/lib/python3.13/site-packages/`. No `sudo` needed 🙅‍♂️.

#### Freeze Dependencies

It's very important to freeze dependencies before sharing your project or deploying it:

```bash
    pip freeze > requirements.txt
```

This creates (or overwrites) `requirements.txt` with exact versions of everything installed:

```
asgiref==3.5.0
Django==4.0.1
numpy==1.22.3
pandas==1.4.1
requests==2.27.1
...
```

Later, another dev (or your server) can just do `pip install -r requirements.txt` inside another activated venv and get the exact same setup.

#### Run Your Project

Just as usual:

```bash
python manage.py runserver   # if Django
python app.py                # if Flask
python myscript.py           # any script
```

### Step 4: Deactivate the Virtual Environment

When you're done for the day (or switching projects):

```bash
deactivate
```

Your prompt changes back:

```
(myenv) user@macbook ~/Projects/MyAwesomeDjangoProject $
user@macbook ~/Projects/MyAwesomeDjangoProject $
```

Now you're back to the system/global Python and packages.

## More `pip` Commands

- **Upgrade pip itself** (do this right after activating):

```bash
pip install --upgrade pip
```

- **List installed packages:**

```bash
pip list
```

or

```bash
pip freeze
```

- **Remove a package:**

```bash
pip uninstall requests
```

- **Check where you are** (very paranoid, but useful):

```bash
which python
```

Should say something like `/Users/yourname/Projects/MyAwesomeDjangoProject/myenv/bin/python`

or

```python
python -c "import sys; print(sys.executable)"
```

Same output.

- **Delete the whole virtual environment** (rare, but happens):

Just `rm -rf myenv` (⚠️ be careful with `rm -rf`). That's it. All gone. Create a new one if needed.

## Tips for macOS Users

- If you installed Python via Homebrew (`brew install python`), your "base" Python is probably the latest (3.13). Verify with `python3 --version`.
- In VSCode, install the "Python" extension, then Cmd + Shift + P → "Python: Select Interpreter" and point it to your `myenv/bin/python`.
- Keep your venv inside your project directory (like `myproject/.venv/`). Don't put it in `~/venvs/` or somewhere global — defeats the purpose 😄.
- Add `*.venv/` or `myenv/` to your project's `.gitignore` file. You don't version-control the venv itself, only `requirements.txt`.

## iCloud Tips

- Use "keep downloaded" for the repo. Ensure all files are synchronized.

## Notes for neoclassical.ai Users

- `neoclassical.ai` is the directory where the virtual environments (plural) exist.
- A virtual environment needs to be activated before installing packages so as not to change system files.
- Each laptop must have its own virtual environment to prevent stepping on one another.

Example setup for `neoclassical.ai`:

```bash
python3 -m venv .venv_air
source .venv_air/bin/activate

python3 -m venv .venv_pro
source .venv_pro/bin/activate

# Then install packages in the active venv
python3 -m pip install matplotlib
```
