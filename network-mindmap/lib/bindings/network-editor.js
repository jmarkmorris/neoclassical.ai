// network-editor.js - Custom functions for network editing
// This version uses a simpler, direct edit approach

// Initialize variables
let firstNodeSelected = null;
let selectedEdge = null;
let isEditing = false;
let activeEditNode = null;

// Function to initialize the network editor
function initNetworkEditor(network, nodes, edges) {
    console.log("Network editor initialized");
    
    // Add a double-click event handler for node editing
    network.on("doubleClick", function(params) {
        console.log("Double-click event:", params);
        if (params.nodes && params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            startNodeEdit(nodeId, network, nodes);
            // Prevent event from bubbling
            params.event.preventDefault();
            params.event.stopPropagation();
        }
    });
    
    // Single-click handler for node selection and edge creation
    network.on("click", function(params) {
        // If we're in edit mode, ignore the click
        if (isEditing) return;
        
        if (params.nodes && params.nodes.length > 0) {
            // Node clicked
            const nodeId = params.nodes[0];
            handleNodeClick(nodeId, network, nodes, edges);
        } else if (params.edges && params.edges.length > 0) {
            // Edge clicked
            selectedEdge = params.edges[0];
            firstNodeSelected = null;
        } else {
            // Background clicked
            firstNodeSelected = null;
            selectedEdge = null;
        }
    });
    
    // Add keyboard handler for the document
    document.addEventListener("keydown", function(event) {
        // Delete key pressed with an edge selected
        if ((event.key === "Delete" || event.key === "Backspace") && selectedEdge && !isEditing) {
            const edgeData = edges.get(selectedEdge);
            if (edgeData) {
                deleteEdge(edgeData, edges);
            }
        } 
        // Escape key pressed
        else if (event.key === "Escape") {
            if (isEditing) {
                // Cancel node editing
                cancelNodeEdit(network);
            } else {
                // Cancel link creation
                firstNodeSelected = null;
                selectedEdge = null;
            }
        }
        // Enter key pressed while editing
        else if (event.key === "Enter" && isEditing && !event.shiftKey) {
            event.preventDefault();
            finishNodeEdit(network, nodes);
        }
    });
}

// Handle node click for linking
function handleNodeClick(nodeId, network, nodes, edges) {
    if (firstNodeSelected !== null) {
        // Second node clicked, create a link if not the same node
        if (firstNodeSelected !== nodeId) {
            createLink(firstNodeSelected, nodeId, edges);
        }
        firstNodeSelected = null;
    } else {
        // First node clicked, store it
        firstNodeSelected = nodeId;
    }
}

// Create a link between nodes
function createLink(fromId, toId, edges) {
    try {
        // Add to visualization
        edges.add({
            from: fromId,
            to: toId
        });
        
        // Save to server
        fetch('/add_edge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source: fromId,
                target: toId
            })
        }).then(response => response.json())
        .catch(error => console.error('Error saving edge:', error));
    } catch (error) {
        console.error("Error creating link:", error);
    }
}

// Delete an edge
function deleteEdge(edgeData, edges) {
    // Remove from visualization
    edges.remove(selectedEdge);
    selectedEdge = null;
    
    // Delete from server
    fetch('/delete_edge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            from: edgeData.from,
            to: edgeData.to
        })
    }).then(response => response.json())
    .catch(error => console.error('Error deleting edge:', error));
}

// Begin editing a node's text
function startNodeEdit(nodeId, network, nodes) {
    console.log("Starting node edit for", nodeId);
    isEditing = true;
    activeEditNode = nodeId;
    
    // Get current node data
    const node = nodes.get(nodeId);
    
    // Create edit input directly in the node
    const input = document.createElement("div");
    input.id = "node-edit-input";
    input.contentEditable = "true";
    input.style.position = "absolute";
    input.style.zIndex = "999";
    input.style.backgroundColor = node.color || "#ffffff";
    input.style.color = "#ffffff";
    input.style.minWidth = "100px";
    input.style.minHeight = "50px";
    input.style.padding = "5px";
    input.style.border = "2px solid red";
    input.style.borderRadius = "3px";
    input.style.boxShadow = "0 0 10px rgba(0,0,0,0.5)";
    input.style.outline = "none";
    input.style.overflow = "hidden";
    input.style.textAlign = "center";
    input.style.fontFamily = "Arial";
    input.style.fontSize = "14px";
    
    // Position the input at the node's position
    const nodePosition = network.getPositions([nodeId])[nodeId];
    const canvasPosition = network.canvasToDOM(nodePosition);
    input.style.left = (canvasPosition.x - 50) + "px";
    input.style.top = (canvasPosition.y - 25) + "px";
    
    // Set the current label
    input.textContent = node.label || "";
    
    // Add to DOM - add to the network container
    const container = network.body.container;
    container.appendChild(input);
    
    // Focus and select all text
    setTimeout(() => {
        input.focus();
        document.execCommand('selectAll', false, null);
    }, 0);
    
    // Add blur event to save
    input.addEventListener("blur", function() {
        finishNodeEdit(network, nodes);
    });
}

// Complete the node editing
function finishNodeEdit(network, nodes) {
    if (!isEditing || !activeEditNode) return;
    
    const input = document.getElementById("node-edit-input");
    if (!input) return;
    
    // Get the text and update the node
    const newLabel = input.textContent.trim();
    nodes.update({
        id: activeEditNode,
        label: newLabel
    });
    
    // Save to server
    fetch('/update_node', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: activeEditNode,
            label: newLabel
        })
    }).then(response => response.json())
    .catch(error => console.error('Error updating node:', error));
    
    // Clean up
    cancelNodeEdit(network);
}

// Cancel node editing without saving
function cancelNodeEdit(network) {
    const input = document.getElementById("node-edit-input");
    if (input && input.parentNode) {
        input.parentNode.removeChild(input);
    }
    
    isEditing = false;
    activeEditNode = null;
}