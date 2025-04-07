# Godot Development Notes

This document outlines strategies and considerations for developing Godot projects, focusing on a programmatic approach assisted by AI tools like `aider` within a VS Code environment. The primary goal is to minimize reliance on the Godot Editor GUI for setup and scene construction, using it mainly for running and visualizing the results.

## Goal: Programmatic Godot Workflow with AI Assistance

The aim is to explore an integrated workflow using:

*   **VS Code:** Primary code editor.
*   **Aider / AI:** For code generation, refactoring, and potentially understanding project structure.
*   **Godot Engine:** Primarily for running the project and visual feedback, minimizing direct GUI manipulation for setup.

This involves investigating:

*   The extent to which Godot project setup and scene creation can be fully automated or scripted.
*   Developing helper scripts (e.g., for asset processing or scene generation) if needed.
*   Leveraging AI capabilities, including multimodal input (like pasting images for analysis) if applicable.
*   Understanding Godot's features for code reuse (e.g., autoloads, custom classes, potentially libraries).

## Programmatic Project Setup Feasibility

Most initial Godot project setup steps *can* be achieved programmatically, though the complexity varies.

### 1. Creating the Project Folder

*   **GUI:** Manual creation via Finder/Explorer.
*   **Programmatic:** Straightforward using standard shell commands.
    ```bash
    mkdir ~/Projects/MyGodotProject
    cd ~/Projects/MyGodotProject
    ```

### 2. Creating `project.godot`

*   **GUI:** Handled by the "New Project" button in the Godot Project Manager.
*   **Programmatic:** Feasible. `project.godot` is an INI-like text file. A minimal version can be generated via scripts or `echo`.
    ```ini
    ; Engine configuration file.
    ; It's best edited using the editor UI and not directly,
    ; unless you know what you're doing.

    config_version=5

    [application]

    config/name="MyProgrammaticProject"
    config/version="1.0"
    config/features=PackedStringArray("4.2", "GL Compatibility")
    config/icon="res://icon.svg"
    ```
    *   **Recommendation:** Maintain a template `project.godot` file with preferred default settings and copy/modify it as needed. Remember to include the default `icon.svg`.

### 3. Setting Project Settings

*   **GUI:** Done via the Project Settings dialog (Project -> Project Settings...).
*   **Programmatic:** Yes, by adding/modifying key-value pairs in `project.godot`.
    *   Example (Setting Default Clear Color to Indigo):
        ```ini
        [rendering]

        environment/defaults/default_clear_color=Color(0.294118, 0, 0.509804, 1)
        ```
    *   **Discovery:** The easiest way to find the correct keys and value formats is often to set the desired option in the GUI and then inspect the changes in `project.godot`.

### 4. Creating GDScript Files (`.gd`)

*   **GUI:** Attaching a new script via the Inspector or Scene tree.
*   **Programmatic:** Simple. `.gd` files are plain text. They can be created and populated using standard file I/O operations in any scripting language or via shell commands.
    ```gdscript
    # Example: angle_path_scene.gd
    extends Node2D

    func _ready():
        print("Scene ready!")

    # Add other functions...
    ```

### 5. Creating Scene Files (`.tscn`) Programmatically via Templates

*   **GUI:** Adding nodes, configuring them, and saving the scene (Scene -> Save Scene).
*   **Programmatic Challenge:** `.tscn` files use a specific text format (`PackedScene`) that includes node hierarchies, properties, signal connections, and unique resource identifiers (`uid://...`, `id="..."`). Generating this format correctly from scratch in code is complex and error-prone, especially for non-trivial scenes.
*   **Recommended Programmatic Approach: Template Substitution**
    1.  **Create a Base Template:** Use the Godot editor to create a minimal scene representing the common starting point for your programmatically generated scenes. Include the essential root node and potentially attach a placeholder script. Save this file (e.g., `templates/base_scene_template.tscn`).
    2.  **Identify Placeholders:** Examine the template `.tscn` file and identify the parts that need to be unique for each generated scene. Use distinct placeholder strings for these parts. Common placeholders include:
        *   The path to the specific script (`ExtResource` path).
        *   The unique ID for the script resource (`ExtResource` id).
        *   The name of the root node (`[node name="..."]`).
        *   The scene's unique ID (`[gd_scene uid="..."]`) - *optional, often reusable*.
    3.  **Write a Substitution Script:** Create a script (e.g., in Python or GDScript) that performs these actions:
        *   Reads the content of the template `.tscn` file.
        *   Uses string replacement functions to substitute the placeholder strings with the actual values for the new scene (e.g., the correct script path, a generated resource ID, the desired node name).
        *   Writes the modified content to a new `.tscn` file in the appropriate project location.

*   **Example Template (`templates/base_scene_template.tscn`):**
    ```gdscene
    ; Template for a basic 2D scene with a script
    [gd_scene load_steps=2 format=3 uid="uid://__TEMPLATE_SCENE_UID__"] ; Placeholder UID (often reusable)

    ; Placeholder for the script resource
    [ext_resource type="Script" path="__SCRIPT_PATH__" id="__SCRIPT_ID__"]

    ; Placeholder for the root node name and script attachment
    [node name="__ROOT_NODE_NAME__" type="Node2D"]
    script = ExtResource("__SCRIPT_ID__")

    ; Add other common nodes or settings below if needed
    ```
    *   **Placeholders to Replace:** `__TEMPLATE_SCENE_UID__`, `__SCRIPT_PATH__`, `__SCRIPT_ID__`, `__ROOT_NODE_NAME__`.

*   **Benefits:** This method leverages the editor for creating the valid base structure and avoids the complexities of generating the `.tscn` format manually. It focuses the programmatic effort on simple string manipulation.

*   **Alternative - Runtime Instantiation:** For scenes where the structure is entirely dynamic or data-driven, creating nodes directly in GDScript (e.g., using `.new()` in `_ready()` or other functions) is also a valid programmatic approach. This bypasses the need for `.tscn` files altogether for that specific content.

### 6. Attaching Scripts to Nodes (in `.tscn`)

*   **GUI:** Drag-and-drop or using the "Attach Script" button.
*   **Programmatic:**
    *   **Via `.tscn` Generation/Templating:** Ensure the `script = ExtResource(...)` line and the corresponding `[ext_resource]` definition are correctly included in the generated/modified `.tscn` file content.
    *   **Via Code:** If creating nodes programmatically at runtime (e.g., in `_ready()`), use `set_script()`:
        ```gdscript
        var my_node = Node2D.new()
        my_node.name = "MyProgrammaticNode"
        var my_script = load("res://my_script.gd")
        my_node.set_script(my_script)
        add_child(my_node)
        ```

### Godot Command-Line Interface (CLI)

*   The Godot executable has CLI arguments, but they are primarily for *running* the editor, games, export processes, or executing specific scripts (`--run`, `--export`, `--script`) within an *existing* project context.
*   It does **not** have high-level commands to bootstrap a new project structure (e.g., `godot --create-project MyProject --template basic_2d`). Project creation relies on the Project Manager GUI or the programmatic methods described above.

## Project Directory and File Organization

A standard Godot project requires a dedicated directory containing at minimum:

*   `project.godot`: The core configuration file defining the project and its settings.
*   `icon.svg`: The default engine icon (can be replaced).

All assets and scripts within the project are referenced using the `res://` prefix, which maps to the project's root directory (where `project.godot` resides).

**Organizing Multiple Examples:**

When converting multiple distinct examples (like separate Python scripts/visualizations) to Godot, you have a few organizational options:

1.  **Separate Godot Project per Example (Recommended):**
    *   Create a unique directory for each example you convert. Each directory will contain its own `project.godot` file and all related scenes (`.tscn`), scripts (`.gd`), and assets.
    *   **Pros:** Clean separation of concerns, independent project settings, easier management of individual examples. This aligns well with how Godot projects are typically structured.
    *   **Cons:** Can lead to many small project directories. Requires opening different projects in Godot to work on different examples.
    *   **Example Structure:**
        ```
        godot_examples/
        ├── Example1/
        │   ├── project.godot
        │   ├── icon.svg
        │   ├── example1_scene.tscn
        │   └── example1_script.gd
        └── Example2/
            ├── project.godot
            ├── icon.svg
            ├── example2_scene.tscn
            └── example2_script.gd
        ```

For converting distinct Python examples, the **separate project approach (Option 1)** is generally preferred for clarity and isolation.

**Internal Project Structure:**

Within a specific Godot project directory, common subdirectories include:

*   `scenes/`: To store `.tscn` files.
*   `scripts/`: To store `.gd` script files.
*   `assets/`: For images, models, fonts, audio, etc.
*   `addons/`: For Godot plugins/addons.
*   `templates/`: (As discussed earlier) For storing `.tscn` or other template files used in programmatic generation.

Using a clear internal structure helps keep larger projects manageable.

## AI-Assisted Workflow (Aider/AI + VS Code + Godot)

Using an AI assistant in your Godot development workflow offers potential benefits but also has limitations to consider:

**Strengths:**

*   **GDScript Generation:** AI is generally proficient at generating GDScript code for specific functions, algorithms, or boilerplate tasks based on descriptions.
*   **Refactoring:** Assisting with restructuring code, improving readability, and applying best practices within `.gd` files.
*   **Explaining Concepts:** Providing explanations for Godot API usage, concepts (signals, groups, scene tree), or GDScript syntax.
*   **Debugging Logic:** Helping to identify logical errors or suggest debugging approaches within script code.
*   **Parsing Text Formats:** AI can potentially assist in understanding or even generating the text-based `project.godot` or simple `.tscn` structures, although precision is key.

**Challenges & Considerations:**

*   **Visual Context:** AI lacks the visual understanding of the Godot editor. Describing scene layouts, node positions, or visual effects purely through text can be challenging and less efficient than using the GUI.
*   **Scene Tree Complexity:** Managing complex scene trees, node relationships, signals, and unique node paths programmatically requires careful planning. AI might struggle to maintain perfect context for intricate scene interactions without seeing the editor.
*   **Godot API Nuances:** While AI can access documentation, it might sometimes generate code that uses outdated APIs, misunderstands specific node behaviors, or isn't the most idiomatic Godot way to achieve a task. Verification is crucial.
*   **Debugging Visual Issues:** Debugging problems related to rendering, layout, animation timing, or physics often requires the visual feedback and debugging tools provided by the Godot editor.
*   **`.tscn` File Integrity:** Programmatically generating or modifying `.tscn` files requires high precision. Small syntax errors or incorrect IDs can easily corrupt the scene file, making it unopenable in the editor. The template approach mitigates this risk.

**Recommendations for an AI-Assisted Programmatic Workflow:**

1.  **Hybrid Approach:** Embrace a mix of programmatic setup and minimal GUI interaction.
    *   **Programmatic:** Handle project creation (`project.godot`), script (`.gd`) generation/modification, and potentially scene generation using templates or runtime instantiation.
    *   **GUI:** Use the Godot editor for:
        *   Initial setup of template `.tscn` files.
        *   Running and visually debugging the project.
        *   Inspecting the scene tree and node properties when troubleshooting.
        *   Fine-tuning visual aspects (colors, positions, animations) where programmatic control is cumbersome.
2.  **Leverage AI for Code:** Focus AI assistance on GDScript logic, algorithms, refactoring, and API usage questions.
3.  **Use Templates for Scenes:** Prefer the `.tscn` template substitution method for creating predefined scene structures programmatically.
4.  **Runtime Instantiation for Dynamic Content:** Create nodes directly in code (`_ready()`, etc.) when the structure is highly dynamic or data-driven.
5.  **Version Control:** Use Git diligently to track changes, especially when programmatically modifying project or scene files.
6.  **Clear Prompts:** Provide clear, specific prompts to the AI, including context about the scene structure or relevant GDScript code snippets.

## Reusable Code Strategies in Godot

Godot offers several ways to create reusable code, suitable for different scopes and complexity levels.

**1. Intra-Project Reuse (Within a Single Project):**

*   **`class_name` Scripts:** The primary method for creating reusable components within a project. Define a script with `class_name MyCustomNode extends Node2D` or `class_name MyDataContainer extends RefCounted`. This makes the script a distinct type that can be instantiated (`MyCustomNode.new()`) or selected directly in the editor's "Add Node" dialog (if inheriting from Node). Ideal for custom nodes, data structures, and utility classes used throughout one project.
*   **Autoloads (Singletons):** Scripts or scenes loaded automatically when the project starts, providing globally accessible objects. Perfect for managing global state (e.g., game settings, player score), providing universally needed functions (e.g., a `MathUtils` singleton), or implementing event buses. Configure them in `Project -> Project Settings -> Autoload`.

**2. Inter-Project Reuse (Sharing Between Separate Projects):**

Based on the goal of sharing GDScript code (custom nodes, data structures, algorithms) between multiple separate Godot projects with a preference for low complexity:

*   **Godot Addons (using GDScript) (Recommended):** This is the standard Godot approach for packaging reusable code and scenes.
    *   **How:** Structure your shared GDScript files (using `class_name`), custom scenes (`.tscn`), and assets within a dedicated directory inside the `addons/` folder (e.g., `addons/my_shared_lib/`). Create a simple `plugin.cfg` file in that directory to define the addon.
    *   **Usage:** To use the shared code in another project, simply copy the `addons/my_shared_lib/` folder into the target project's `addons/` directory. Then, enable the plugin via `Project -> Project Settings -> Plugins`.
    *   **Pros:** Idiomatic Godot solution, keeps shared code organized and self-contained, integrates well with the editor (custom types can appear in menus), uses only GDScript, relatively low complexity.
    *   **Cons:** Requires understanding the `addons/` structure and creating the `plugin.cfg` file (minimal effort).

*   **Manual Copying / Symlinking:** The simplest method.
    *   **How:** Maintain a central directory outside your projects containing your shared `.gd` files (using `class_name`). Manually copy these files/folders into each project that needs them, or use symbolic links (`ln -s` on macOS/Linux) to point from within each project to the central shared directory/files.
    *   **Pros:** Lowest setup complexity.
    *   **Cons:** Requires manual synchronization of copied files. Symlinks can sometimes be less intuitive or robust depending on tools and OS. Poorer editor integration compared to addons.

*   **Other Options (Less Suitable for Current Goals):**
    *   **C#:** Allows creating shared DLLs but increases complexity and moves away from GDScript.
    *   **GDExtension:** Powerful for native code integration but significantly more complex than desired.

## Future Exploration

*   Develop a core Godot Addon (`neoclassical_core`?) containing common GDScript classes and nodes for point potentials, path tracing, and wave visualization.
*   Explore helper scripts (Python or GDScript using `--script`) for automating the creation of new Godot example projects based on templates and incorporating the core addon.
                                                                                                                         
=======                                                                                                                                                                              
                                                                                                                         
