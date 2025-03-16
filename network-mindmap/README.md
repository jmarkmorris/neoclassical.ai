# Interactive Network Mindmap with PyVis and Flask

This application provides a web-based interface for creating and interacting with network visualizations using PyVis and Flask. It allows users to add nodes and edges dynamically, and customize the physics simulation parameters.

## Features

- Add nodes with custom labels and colors
- Create edges between existing nodes
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

3. Save the files with the following structure:

```
interactive-network/
├── app.py
├── templates/
│   └── index.html
└── static/
    # This directory will be created automatically if it doesn't exist
```

## Running the Application

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://127.0.0.1:5000/
```

3. You should see the interactive network visualization interface.

## Usage

### Adding Nodes
1. Enter a label for your new node in the "Node Label" field
2. Choose a color using the color picker
3. Click "Add Node"

### Adding Edges
1. Select a source node from the "From Node" dropdown
2. Select a target node from the "To Node" dropdown
3. Click "Add Edge"

### Adjusting Physics Settings
1. Toggle the "Physics Enabled" checkbox to turn the physics simulation on or off
2. Adjust the "Spring Constant" slider to change the strength of the spring forces
3. Adjust the "Gravitational Constant" slider to change the strength of the gravitational forces
4. Click "Update Network" to apply your changes

### Interacting with the Network
- Click and drag nodes to reposition them
- Scroll to zoom in and out
- Click and drag the background to pan the view

## Customization

You can modify the `app.py` file to change the initial network configuration, add more node properties, or customize the physics simulation parameters.

## Troubleshooting

If you encounter any issues with the application:

1. Make sure you have all the required packages installed
2. Check that the Flask application is running and accessible
3. Look for any error messages in the console where you started the Flask app
4. Try clearing your browser cache or using a different browser

If you continue to experience problems, please open an issue on GitHub.

