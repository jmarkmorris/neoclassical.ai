 # Godot Development Notes

This document outlines strategies and considerations for developing Godot projects, focusing on a programmatic approach potentially assisted by AI tools like `aider` with LLM models within a VS Code environment. The primary goal is to minimize reliance on the Godot Editor GUI for setup and scene construction, using it mainly for running and visualizing the results.

## Goal: Programmatic Godot Workflow

The aim is to explore an integrated workflow using:

*   **VS Code:** Primary code editor.
*   **Aider / AI:** For code generation, refactoring, and potentially understanding project structure.
*   **Godot Engine:** Primarily for running the project and visual feedback, minimizing direct GUI manipulation for setup.

This involves investigating:

*   The extent to which Godot project setup and scene creation can be fully automated or scripted.
*   Developing helper scripts (e.g., for asset processing or scene generation) if needed.
*   Leveraging AI capabilities, including multimodal input (like pasting images for analysis) if applicable.
*   Understanding Godot's features for code reuse (e.g., autoloads, custom classes, potentially libraries).

---

## Godot Installation

If Godot gets corrupted, reinstall it from https://godotengine.org/.

## Initialize a Bare Bones Project

Here’s how you can create a bare-bones Godot Engine project with a single `Node3D`:

### Step-by-Step Instructions

1. **Launch Godot Engine**:
   Open the Godot Engine application on your computer.

2. **Create a New Project**:
   - On the project manager screen, click on **“New Project”**.
   - In the **Project Path** field, input the desired directory path: `/Users/markmorris/Documents/NPQG_Code_Base/neoclassical.ai/examples/CircleSizes`.
   - Name the project as `CircleSizes`. (no, it won't create `.../CircleSizes/CircleSize/...`)
   - Click **“Create Folder”** to ensure the directory is created, then click **“Create & Edit”** to proceed.

3. **Set Up the Base Node**:
   - In the Godot editor, go to the **Scene** panel and click **“+”** to create a new node.
   - Select **Node3D** from the node list (you can search for it in the search bar).
   - This will create a single `Node3D` object in the scene tree.

4. **Set Up Background Color**:
   - Go to the **Project** menu and choose **Project Settings**
   - Go to **Rendering** and then **Environment**
   - Click on the color bar for **Default Clear Color**
   - A color selector pops up. I like INDIGO which is #4B0082.
   - Click on **Close**

5. **Set Up Screen Resolution and Display Window**
   - Go to the **Project** menu and choose **Project Settings**
   - Go to **Display** and then **Window**
   - Under **Size** enter 1920 × 1080
   - Set **Mode** to fullsize.

6. **Save the Scene**:
   - Since you’re planning to add everything programmatically later, you don’t need to modify the scene further.
   - Save the empty scene to preserve the `Node3D` as the root. 
   - Click **Scene** > **Save Scene**, and name it `main.tscn` (or leave the default name). 
   - The tscn file will look like this:

        ```
        cat node_3d.tscn
        [gd_scene format=3 uid="uid://7xu24s130gkk"]
        [node name="Node3D" type="Node3D"]
        ```

   - Your project will now be initialized in `/Users/markmorris/Documents/NPQG_Code_Base/neoclassical.ai/examples/CircleSizes` with a minimal setup. 

7. **Ensure Minimal Setup**:
   - Avoid manually creating `.gd` script files or adding additional nodes. 
   - The initial project will remain empty apart from the single `Node3D`.

8. **Check the Files**:
   - Godot automatically creates necessary files such as `project.godot` (project configuration) in the project directory.

9. **Ready for Programmatic Development**:
   - You can now start building your project programmatically. 
   - Use Aider/LLM to add nodes, scenes, or any functionality as needed.

---



### Enable automatic reloading of files that have changed on disk by adjusting the editor settings. Here's how:

* Go to Editor Settings in the Godot editor.
* Navigate to Text Editor > Behavior.
* Turn on advanced settings
* Look for the option Auto Reload Scripts on External Change and set it to On.

### Running/Opening a Visualization

* Import or Scan for the Project
* In the FileSystem dock (lower-left) open the main scene (e.g., `main.tscn`) by double-clicking it.
* Click on the 'run' icon in the upper right.

---

## Project Organization

Proper file and directory structure is crucial for maintainability.

### Basic Project Structure

A standard Godot project requires a dedicated directory containing at minimum:

*   `main.tscn`: The main scene.
*   `project.godot`: The core configuration file defining the project and its settings.
*   `icon.svg`: The default engine icon (can be replaced).

All assets and scripts within the project are referenced using the `res://` prefix, which maps to the project's root directory (the directory containing `project.godot`).

### Organizing Multiple Examples

    *   Create a unique directory for each project. 
    *   Each directory will contain its own `project.godot` file and all related scenes (`.tscn`), scripts (`.gd`), and assets.
    *   **Pros:** Clean separation of concerns, independent project settings, easier management of individual examples. 
    *   This aligns well with how Godot projects are typically structured.
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

### Internal Project Structure

Within a large Godot project directory, common subdirectories include:

*   `scenes/`: To store `.tscn` files.
*   `scripts/`: To store `.gd` script files.
*   `assets/`: For images, models, fonts, audio, etc.
*   `addons/`: For Godot plugins/addons.
*   `templates/`: For storing template files used in programmatic generation.

Using a clear internal structure helps keep larger projects manageable.

---

## AI-Assisted Workflow (Aider/AI + VS Code + Godot)

Using an AI assistant like `aider` in your Godot development workflow offers potential benefits but also has challenges:

*   **GDScript Generation:** AI is generally proficient at generating GDScript code for specific functions, algorithms, or boilerplate tasks based on descriptions.
*   **Refactoring:** Assisting with restructuring code, improving readability, and applying best practices within `.gd` files.
*   **Explaining Concepts:** Providing explanations for Godot API usage, concepts (signals, groups, scene tree), or GDScript syntax.
*   **Debugging Logic:** Helping to identify logical errors or suggest debugging approaches within script code.
*   **Parsing Text Formats:** AI can potentially assist in understanding or even generating the text-based `project.godot` or simple `.tscn` structures, although precision is crucial.
*   **Visual Context:** Describing scene layouts, node positions, or visual effects purely through text can be challenging. Include goal images. Add current state images and request review, comparison to goal, and revised code.
*   **Scene Tree Complexity:** Managing complex scene trees, node relationships, signals, and unique node paths programmatically requires careful planning. AI might struggle to maintain perfect context for intricate scene interactions without seeing the editor.
*   **Godot API Nuances:** While AI can access documentation, it might sometimes generate code that uses outdated APIs, misunderstands specific node behaviors, or isn't the most idiomatic Godot way to achieve a task. Verification is crucial.
*   **Debugging Visual Issues:** Debugging problems related to rendering, layout, animation timing, or physics often requires the visual feedback and debugging tools provided by the Godot editor.
*   **`.tscn` File Integrity:** Programmatically generating or modifying `.tscn` files requires high precision. Small syntax errors or incorrect IDs can easily corrupt the scene file, making it unopenable in the editor. The template substitution approach significantly mitigates this risk.

### Recommendations for an AI-Assisted Programmatic Workflow

1.  **Hybrid Approach:** Embrace a mix of programmatic setup and minimal GUI interaction.
    *   **Programmatic:** Handle project creation (`project.godot`), script (`.gd`) generation/modification, and potentially scene generation using templates or runtime instantiation.
    *   **GUI:** Use the Godot editor for:
        *   Initial setup of template `.tscn` files.
        *   Running and visually debugging the project.
        *   Inspecting the scene tree and node properties when troubleshooting.
        *   Fine-tuning visual aspects (colors, positions, animations) where programmatic control is cumbersome.
2.  **Leverage AI for Code:** Focus AI assistance on GDScript logic, algorithms, refactoring, and API usage questions.
4.  **Runtime Instantiation for Dynamic Content:** Create nodes directly in code (`_ready()`, etc.) when the structure is highly dynamic or data-driven.
5.  **Version Control:** Use Git diligently to track changes, especially when programmatically modifying project or scene files.
6.  **Clear Prompts:** Provide clear, specific prompts to the AI, including context about the scene structure, relevant GDScript code snippets, and desired outcomes.

---

## Reusable Code Strategies in Godot

Godot offers several ways to create reusable code, suitable for different scopes and complexity levels.

### 1. Intra-Project Reuse (Within a Single Project)

*   **`class_name` Scripts:** The primary method for creating reusable components within a project. Define a script with `class_name MyCustomNode extends Node2D` or `class_name MyDataContainer extends RefCounted`. This makes the script a distinct type that can be instantiated (`MyCustomNode.new()`) or selected directly in the editor's "Add Node" dialog (if inheriting from Node). Ideal for custom nodes, data structures, and utility classes used throughout one project.
*   **Autoloads (Singletons):** Scripts or scenes loaded automatically when the project starts, providing globally accessible objects. Perfect for managing global state (e.g., game settings, player score), providing universally needed functions (e.g., a `MathUtils` singleton), or implementing event buses. Configure them via `Project -> Project Settings -> Autoload`.

### 2. Inter-Project Reuse (Sharing Between Separate Projects)

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

---

# Godot Tools VsCode Extension

## GDScript (.gd) language features:

- syntax highlighting
- ctrl+click on any symbol to jump to its definition or open its documentation
- ctrl+click on res://resource/path links
- hover previews on res://resource/path links
- builtin code formatter
- autocompletions
- full typed GDScript support
- optional "Smart Mode" to improve productivity with dynamically typed scripts
- Hover previews show function/variable definitions including doc-comments
- switch from a .gd file to the related .tscn file (default keybind is alt+o)
- display script warnings and errors

## The extension adds a few entries to the VS Code Command Palette under "Godot Tools":

- Open workspace with Godot editor
- List Godot's native classes (and open their documentation)
- Debug the current .tscn/.gd file
- Debug the pinned .tscn/.gd file
- Pin/Unpin the current .tscn/.gd file for debugging
- Open the pinned file

---

# GUI Project Setup and Workflow (Minimal)

While the goal is a programmatic workflow, sometimes minimal GUI setup is the quickest way to establish the basic project structure before switching to code. Use the GUI primarily for initial setup and visualization.

## 1. Create a New Project

*   **Choose Name:** Decide on a `<name>` for your project or tool (e.g., `ParticleSimulator`).
*   **Open Godot:** Launch the Godot Project Manager.
*   **New Project:** Click the "New Project" button.
*   **Project Path:** Enter a valid directory path for your project *ending* in the chosen `<name>`. For example, `~/GodotProjects/ParticleSimulator`. **Important:** Do *not* create the directory beforehand; Godot will do this.
*   **Renderer:** Select a renderer (e.g., "Forward+").
*   **Create & Edit:** Click the "Create & Edit" button. Godot will create the directory, the `project.godot` file, `icon.svg`, and open the editor.

## 2. Adjust Project Settings (Optional but Recommended)

*   **Window Settings:** Go to `Project -> Project Settings -> Display -> Window`. Adjust `Width`, `Height`, `Stretch Mode`, etc., if needed.
*   **Background Color:** Go to `Project -> Project Settings -> Rendering -> Environment`. Click the `Default Clear Color` property and set it to your desired color (e.g., INDIGO #4B0082). Click "Close".

## 3. Create and Save the Main Scene

*   **New Scene:** In the main editor window, click the "Scene" menu -> "New Scene".
*   **Add Root Node:** In the "Scene" dock (usually top-left), click the "+" button ("Add Child Node"). Select an appropriate root node type (e.g., `Node2D` for 2D, `Node3D` for 3D) and click "Create".
*   **Select Root:** Ensure the newly created root node (e.g., `Node2D`) is selected in the Scene dock.
*   **Save Scene:** Click "Scene" menu -> "Save Scene As...". Name the scene file, typically matching your project name (e.g., `particle_simulator.tscn` or `main.tscn`). Save it in the root of your project (`res://`).

Now you have a basic project structure (`project.godot`, `icon.svg`, `<name>.tscn`) and can proceed with programmatic development (adding scripts, nodes via code, etc.).
                                                                                                                         
---

### Defunct - Creating and Using MyGodotTemplate (not reliable due to uid not refreshed)

*Broken* : This method doesn't work because uid is unique per project. It would need to be regenerated. We do need the fonts directory in the MyGodotTemplate if we want to use a font other than the default. Need to rethink how to approach this.

The quickest possible setup is to set up and use a bare bones template using the Step-by-Step instructions below. Let's assume you have set up a project called 'MyGodotTemplate' as examples/MyGodotTemplate.

- cd to neoclassical.ai repo root
- run run-new-godot.sh (which does all of the following)

- cd to the examples directory
- cp -r MyGodotTemplate NewProjectName
- cd NewProjectName
- edit 'project.godot' and replace config/name="MyGodotTemplate" with config/name="NewProjectName"
- go to the Godot app and open NewProjectName, click on the .tscn file, and you are ready to build.
- as an added bonus, the MyGodotTemplate contains a font directory with several fonts and their .tres and .ttf files.