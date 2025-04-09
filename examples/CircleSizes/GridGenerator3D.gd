extends Node3D

# --- Grid Configuration ---
@export var grid_rows: int = 10
@export var grid_cols: int = 15
@export var grid_size: Vector2 = Vector2(14, 8) # World units for total grid width and height
@export var grid_line_color: Color = Color(0.5, 0.2, 0.6, 0.8) # Lighter purple

# --- Node References ---
var mesh_instance: MeshInstance3D = null

func _ready() -> void:
	print("GridGenerator3D: _ready() called.") # DEBUG
	generate_grid_mesh()

func generate_grid_mesh() -> void:
	print("GridGenerator3D: generate_grid_mesh() called.") # DEBUG
	# Create or clear previous mesh instance
	if mesh_instance != null:
		print("GridGenerator3D: Clearing previous mesh instance.") # DEBUG
		mesh_instance.queue_free()

	mesh_instance = MeshInstance3D.new()
	add_child(mesh_instance)

	# Create the mesh resource
	var immediate_mesh: ImmediateMesh = ImmediateMesh.new()

	# Create a material for the lines
	var material: StandardMaterial3D = StandardMaterial3D.new()
	# material.albedo_color = grid_line_color # DEBUG: Use plain white first
	material.albedo_color = Color.WHITE # DEBUG: Use plain white first
	material.albedo_color.a = 1.0 # DEBUG: Ensure fully opaque
	material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED # Make lines ignore lighting
	# material.use_point_size = true # Often not needed for ImmediateMesh lines
	# material.render_priority = 1 # Optional: Render grid on top if needed

	# Start defining the line geometry
	immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINES, material)

	# Calculate step sizes
	var step_x: float = grid_size.x / grid_cols
	var step_y: float = grid_size.y / grid_rows

	# Calculate start offsets (to center the grid around the node's origin)
	var start_x: float = -grid_size.x / 2.0
	var start_y: float = -grid_size.y / 2.0
	var end_x: float = grid_size.x / 2.0
	var end_y: float = grid_size.y / 2.0

	# Add vertices for vertical lines
	for i in range(1, grid_cols):
		var x_pos: float = start_x + i * step_x
		immediate_mesh.surface_add_vertex(Vector3(x_pos, start_y, 0))
		immediate_mesh.surface_add_vertex(Vector3(x_pos, end_y, 0))

	# Add vertices for horizontal lines
	for i in range(1, grid_rows):
		var y_pos: float = start_y + i * step_y
		immediate_mesh.surface_add_vertex(Vector3(start_x, y_pos, 0))
		immediate_mesh.surface_add_vertex(Vector3(end_x, y_pos, 0))

	# Finalize the surface
	immediate_mesh.surface_end()

	# Assign the generated mesh to the MeshInstance3D
	mesh_instance.mesh = immediate_mesh
	mesh_instance.layers = 1 # DEBUG: Ensure it's on the default rendering layer
	print("GridGenerator3D: Mesh generated and assigned to layer 1.") # DEBUG
