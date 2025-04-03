neoclassical.ai is the directory where the virtual environments (plural) exists.
a virtual environment needs to be activated before installing packages so as not to change system files.

each laptop must have its own virtual environment to prevent stepping on one another.

python3 -m venv .venv_air
source .venv_air/bin/activate

python3 -m venv .venv_pro
source .venv_pro/bin/activate

then install packages in the active venv
python3 -m pip install matplotlib

iCloud tips: Use "keep downloaded" for the repo. Ensure all files are synchronized.  

---

# Create    : python3 -m venv myenv
# Activate  : source myenv/bin/activate
# Install   : pip install package_name
# List pkgs : pip list
# Freeze    : pip freeze > requirements.txt
# Deactivate: deactivate
# Delete    : rm -rf myenv

# Step 1: Create the virtual environment itself (this is a one-time action per project):

python3 -m venv myenv

## Important notes:

- We use python3 explicitly because macOS (as of Ventura) ships with Python 2.7 (ancient 😱) as python
- python3 is the one you installed separately (hopefully via brew install python 🙏). 
- If you just installed Python 3.x via Homebrew, python3 is the correct command.
- venv is a module (-m means "treat this as a module, not an executable")
- myenv is just the name (directory) of your virtual environment. 
-- venv (classic, but confusing if you have many projects)
-- .venv (dot makes it hidden by default — I like this, keeps dirs clean) 
-- any-name-you-choose 

Just don't name it venv inside your actual project dir if you're using modern IDEs (PyCharm, VSCode) because they'll get confused 🤪.

This command will silently create a directory myenv (or whatever you named it) containing:

myenv/
├── bin          # <-- this is where the magic happens
│   ├── activate
│   ├── pip
│   ├── pip3
│   ├── python -> python3.10 (or whatever version you have)
│   └── python3 -> python3.10 (symlinks, rejoice!)
├── include
├── lib          # <-- all your packages will live here (site-packages inside)
│   └── python3.10
│       └── site-packages
└── pyvenv.cfg   # <-- config file saying "hey, this is Python 3.10, home is /usr/local/bin/python3.10" etc

# Step 2: Activate the virtual environment

This is the most important step. Until you do this, you're still using the system Python (or the one your shell found first in $PATH). To "enter" your isolated world:

source myenv/bin/activate
(source is a shell built-in meaning "read and execute commands from this file in the current shell", don't confuse with just running myenv/bin/activate which wouldn't work because it needs to modify the current shell's environment).

As soon as you hit Enter, you'll see your command prompt changing:

- user@macbook ~/Projects/MyAwesomeDjangoProject $
+ (myenv) user@macbook ~/Projects/MyAwesomeDjangoProject $
That (myenv) prefix means you're IN. Now:

python will point to myenv/bin/python (not /usr/bin/python or /usr/local/bin/python3)
pip will install packages inside myenv/lib/python3.x/site-packages/ (aha - macair and macpro 2x installs)
Any python you run will use those packages, not the global ones.
What you do while activated (daily work):

## Install packages

Just pip as usual. Example:

pip install requests django==4.0.1 numpy pandas
All go into myenv/lib/python3.10/site-packages/. No sudo needed 🙅‍♂️.

## Freeze dependencies (very important before sharing project or deploying) 

pip freeze > requirements.txt
This creates (or overwrites) requirements.txt with exact versions of everything installed:

asgiref==3.5.0
Django==4.0.1
numpy==1.22.3
pandas==1.4.1
requests==2.27.1
...
Later, another dev (or your server) can just do pip install -r requirements.txt inside another activated venv and get the exact same setup.

## Run your project
Just as usual:

python manage.py runserver   # if Django
python app.py                # if Flask
python myscript.py           # any script

# Step 3: Deactivate (leave the virtual environment)

When you're done for the day (or switching projects):

deactivate
Prompt changes back:

- (myenv) user@macbook ~/Projects/MyAwesomeDjangoProject $
+ user@macbook ~/Projects/MyAwesomeDjangoProject $
Now you're back to system/global Python and packages.

## More pip:

upgrade pip itself (do this right after activating):
pip install --upgrade pip

List installed packages:
pip list
or
pip freeze

Remove a package:
pip uninstall requests
Check where you are (very paranoid, but useful):

which python
- should say something like /Users/yourname/Projects/MyAwesomeDjangoProject/myenv/bin/python
or

python -c "import sys; print(sys.executable)"
- same output

Delete the whole virtual environment (rare, but happens):
- Just rm -rf myenv (⚠️ be careful with rm -rf). That's it. All gone. Create a new one if needed.

Tips for macOS users specifically:

If you installed Python via Homebrew (brew install python), your "base" Python is probably the latest (3.10). Verify with python3 --version.

In VSCode, install the "Python" extension, then Cmd + Shift + P → "Python: Select Interpreter" and point it to your myenv/bin/python.

Keep your venv inside your project directory (like myproject/.venv/). Don't put it in ~/venvs/ or somewhere global — defeats the purpose 😄.

Add *.venv/ or myenv/ to your project's .gitignore file. You don't version-control the venv itself, only requirements.txt.
