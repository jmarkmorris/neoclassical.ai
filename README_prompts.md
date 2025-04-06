# Prompts for Manim

- name the scene the same as the filename (or actually the requested output) to avoid warning.
- do not add comments specific to a problem or issue or reversion
- all comments added should be professional and concise and explanatory of the overall design

When writing code, you MUST follow these principles:

Code should be easy to read and understand.
Keep the code as simple as possible. Avoid unnecessary complexity.
Use meaningful names for variables, functions, etc. Names should reveal intent.
Functions should be small and do one thing well. They should not exceed a few lines.
Function names should describe the action being performed.
Prefer fewer arguments in functions. Ideally, aim for no more than two or three.
Only use comments when necessary, as they can become outdated. Instead, strive to make the code self-explanatory.
When comments are used, they should add useful information that is not readily apparent from the code itself.
Properly handle errors and exceptions to ensure the software's robustness.
Use exceptions rather than error codes for handling errors.
Consider security implications of the code. Implement security best practices to protect against vulnerabilities and attacks.
Adhere to these 4 principles of Functional Programming:
Pure Functions
Immutability
Function Composition
Declarative Code

Convention files are markdown files that specify coding guidelines for aider to follow. They can include preferences like:

Coding style rules
Preferred libraries and packages
Type hint requirements
Testing conventions
Documentation standards
And more
For more information about using conventions with aider, see the conventions documentation.

How to Use These Conventions

Browse the subdirectories to find a conventions file that matches your needs
Copy the desired CONVENTIONS.md to your project
Load it in aider using either:
aider --read-only CONVENTIONS.md
Or add it to your .aider.conf.yml:
read-only: CONVENTIONS.md

Always load conventions
You can also configure aider to always load your conventions file in the .aider.conf.yml config file:

# alone
read: CONVENTIONS.md

# multiple files
read: [CONVENTIONS.md, anotherfile.txt]