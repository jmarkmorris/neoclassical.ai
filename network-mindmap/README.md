# Interactive Network Mindmap with PyVis and Flask

This application provides a web-based interface for creating and interacting with network visualizations using PyVis and Flask. It allows users to create rectangular nodes, add text directly on nodes, and create links between nodes dynamically.

## Features

- Create rectangular nodes with custom colors
- Add and edit text on nodes by double-clicking
- Create links dynamically by clicking between nodes
- Delete links by selecting them and pressing the Delete key
- Toggle physics simulation on/off
- Adjust physics parameters (spring constant and gravitational force)
- Interactive network visualization with drag-and-drop functionality

## Requirements

- Python 3.6+
- Flask
- PyVis
- NetworkX

## Installation

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install the required packages:

```bash
pip install flask pyvis networkx
```

3. Make sure you have the following structure:

```
network-mindmap/
├── app.py
├── lib/
│   └── bindings/
│       ├── utils.js
│       └── network-editor.js
├── templates/
│   └── index.html
└── static/
    # Generated network files will be stored here
```

## Running the Application

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://127.0.0.1:5001/
```

3. You should see the interactive network visualization interface.

## Usage

### Adding Nodes
1. Choose a color using the color picker
2. Click "Add Node" to create a new rectangular node

### Editing Nodes
1. Double-click on any node to add or edit its text
2. Type your content
3. Press Enter or click outside the node to save

### Creating Links
1. Click on a source node (first node)
2. Then click on a target node (second node)
3. A link will be created between them

### Deleting Links
1. Click on a link to select it
2. Press the Delete key to remove it

### Adjusting Physics Settings
1. Toggle the "Physics Enabled" checkbox to turn the physics simulation on or off
2. Adjust the "Spring Constant" slider to change the strength of the spring forces
3. Adjust the "Gravitational Constant" slider to change the strength of the gravitational forces
4. Click "Update Network" to apply your changes

### Interacting with the Network
- Click and drag nodes to reposition them
- Scroll to zoom in and out
- Click and drag the background to pan the view
- Press Escape to cancel the current operation

## Customization

You can modify the `app.py` file to change the initial network configuration, add more node properties, or customize the physics simulation parameters.

## Troubleshooting

If you encounter any issues with the application:

1. Make sure you have all the required packages installed
2. Check that the Flask application is running and accessible
3. Look for any error messages in the console where you started the Flask app
4. Try clearing your browser cache or using a different browser