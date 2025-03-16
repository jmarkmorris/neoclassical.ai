# app.py
from flask import Flask, render_template, request, jsonify
from pyvis.network import Network
import json
import os
import uuid

app = Flask(__name__)

class NetworkManager:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.next_node_id = 1
        self.init_default_network()
    
    def init_default_network(self):
        # Add initial nodes
        colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33"]
        for i in range(1, 5):
            node_id = self.next_node_id
            self.next_node_id += 1
            self.nodes[node_id] = {
                "id": node_id,
                "label": f"Node {node_id}",
                "color": colors[i-1]
            }
        
        # Add initial edges
        self.edges = [
            {"from": 1, "to": 2},
            {"from": 1, "to": 3},
            {"from": 3, "to": 4},
            {"from": 2, "to": 4}
        ]
    
    def add_node(self, label, color):
        node_id = self.next_node_id
        self.next_node_id += 1
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "color": color
        }
        return node_id
    
    def add_edge(self, source, target):
        if int(source) != int(target):  # Prevent self-loops
            edge = {"from": int(source), "to": int(target)}
            if edge not in self.edges:
                self.edges.append(edge)
                return True
        return False
    
    def get_network_data(self):
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges
        }
    
    def generate_html(self, physics_params=None):
        net = Network(height="700px", width="100%", bgcolor="#222222", font_color="white")
        net.barnes_hut()
        
        # Add all nodes
        for node_id, node_data in self.nodes.items():
            net.add_node(node_id, label=node_data["label"], color=node_data["color"], 
                         title=f"Node ID: {node_id}")
        
        # Add all edges
        for edge in self.edges:
            net.add_edge(edge["from"], edge["to"])
        
        # Set physics options
        physics_options = {
            "nodes": {
                "shape": "dot",
                "size": 25,
                "font": {
                    "size": 16,
                    "face": "Tahoma"
                },
                "borderWidth": 2
            },
            "edges": {
                "width": 2,
                "color": {
                    "inherit": True
                },
                "smooth": {
                    "type": "continuous"
                }
            },
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based",
                "enabled": True
            },
            "interaction": {
                "navigationButtons": True,
                "keyboard": True,
                "hover": True,
                "multiselect": True,
                "dragNodes": True,
                "hideEdgesOnDrag": False,
                "hideNodesOnDrag": False
            }
        }
        
        # Update physics if custom parameters provided
        if physics_params:
            if "springConstant" in physics_params:
                physics_options["physics"]["forceAtlas2Based"]["springConstant"] = float(physics_params["springConstant"])
            if "gravitationalConstant" in physics_params:
                physics_options["physics"]["forceAtlas2Based"]["gravitationalConstant"] = float(physics_params["gravitationalConstant"])
            if "physicsEnabled" in physics_params:
                physics_options["physics"]["enabled"] = physics_params["physicsEnabled"]
        
        net.set_options(json.dumps(physics_options))
        
        # Generate unique filename to prevent caching issues
        filename = f"static/network_{uuid.uuid4().hex[:8]}.html"
        net.save_graph(filename)
        return filename

# Initialize our network manager
network_manager = NetworkManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_network', methods=['POST'])
def generate_network():
    data = request.json
    physics_params = {
        "springConstant": data.get("springConstant", 0.08),
        "gravitationalConstant": data.get("gravitationalConstant", -50),
        "physicsEnabled": data.get("physicsEnabled", True)
    }
    
    network_file = network_manager.generate_html(physics_params)
    return jsonify({"network_file": "/" + network_file})

@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.json
    label = data.get('label', 'New Node')
    color = data.get('color', '#3498db')
    
    node_id = network_manager.add_node(label, color)
    return jsonify({
        "success": True, 
        "node_id": node_id,
        "nodes": list(network_manager.nodes.values())
    })

@app.route('/add_edge', methods=['POST'])
def add_edge():
    data = request.json
    source = data.get('source')
    target = data.get('target')
    
    success = network_manager.add_edge(source, target)
    return jsonify({"success": success})

@app.route('/get_network_data')
def get_network_data():
    return jsonify(network_manager.get_network_data())

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True, port=5000)
