extends Node3D

# --- Grid Configuration ---
@export var grid_rows: int = 10
@export var grid_cols: int = 15
@export var grid_size: Vector2 = Vector2(14, 8) # World units for total grid width and height
@export var grid_line_color: Color = Color(0.5, 0.2, 0.6, 0.8) # Lighter purple

# --- Dot Configuration ---
@export var dot_radius: float = 0.2 # Initial fixed radius for all dots
@export var dot_color_red: Color = Color.RED
@export var dot_color_blue: Color = Color.BLUE

# --- Node References ---
var mesh_instance: MeshInstance3D = null
var dots_parent: Node3D = null # Node to hold all dot meshes

func _ready() -> void:
	generate_grid_mesh()
	generate_dots()

func generate_grid_mesh() -> void:
	# Create or clear previous mesh instance
	if mesh_instance != null:
		mesh_instance.queue_free()

	mesh_instance = MeshInstance3D.new()
	add_child(mesh_instance)

	# Create the mesh resource
	var immediate_mesh: ImmediateMesh = ImmediateMesh.new()

	# Create a material for the lines
	var material: StandardMaterial3D = StandardMaterial3D.new()
	material.albedo_color = grid_line_color
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

func generate_dots() -> void:
	# Create or clear parent node for dots
	if dots_parent != null:
		dots_parent.queue_free()
	dots_parent = Node3D.new()
	dots_parent.name = "DotsContainer"
	add_child(dots_parent)

	# Calculate step sizes (same as grid)
	var step_x: float = grid_size.x / grid_cols
	var step_y: float = grid_size.y / grid_rows

	# Calculate start offset for cell centers
	var start_x: float = -grid_size.x / 2.0 + step_x / 2.0
	var start_y: float = -grid_size.y / 2.0 + step_y / 2.0

	# Pre-create mesh and materials (optimization)
	var sphere_mesh: SphereMesh = SphereMesh.new()
	sphere_mesh.radius = dot_radius
	sphere_mesh.height = dot_radius * 2.0 # Standard sphere height

	var red_material: StandardMaterial3D = StandardMaterial3D.new()
	red_material.albedo_color = dot_color_red
	red_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED

	var blue_material: StandardMaterial3D = StandardMaterial3D.new()
	blue_material.albedo_color = dot_color_blue
	blue_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED

	# Iterate through rows and columns to place dots
	for row in range(grid_rows):
		for col in range(grid_cols):
			# Calculate cell center position
			var cell_center_x: float = start_x + col * step_x
			var cell_center_y: float = start_y + row * step_y
			var cell_center_pos: Vector3 = Vector3(cell_center_x, cell_center_y, 0.01) # Slightly offset Z

			# Create MeshInstance for the dot
			var dot_instance: MeshInstance3D = MeshInstance3D.new()
			dot_instance.mesh = sphere_mesh # Reuse the same mesh resource

			# Determine color based on grid position (alternating pattern)
			if (row + col) % 2 == 0:
				dot_instance.material_override = blue_material # Use material override
			else:
				dot_instance.material_override = red_material # Use material override

			# Set position and add to the container
			dot_instance.position = cell_center_pos
			dots_parent.add_child(dot_instance)
