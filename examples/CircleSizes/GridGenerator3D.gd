extends Node3D

# --- Grid Configuration ---
@export var grid_rows: int = 8
@export var grid_cols: int = 14
@export var grid_size: Vector2 = Vector2(14, 8) # World units for total grid width and height
@export var grid_line_color: Color = Color(0.5, 0.2, 0.6, 0.8) # Lighter purple

# --- Dot Configuration ---
@export var start_radius: float = 0.002
@export var radius_increment: float = 0.002
@export var dot_separation_factor: float = 0.3 # How far apart dots are within a cell (fraction of cell width)
@export var dot_color_red: Color = Color.RED
@export var dot_color_blue: Color = Color.BLUE

# --- Label Configuration ---
@export var label_font_size: int = 26 # Adjust as needed for visibility
@export var label_color: Color = Color.WHITE

# --- Positioning Constants ---
const DOT_Z_OFFSET: float = 0.01
const LABEL_Z_OFFSET: float = 0.02
const DOT_VERTICAL_FACTOR: float = 0.05 # Percentage of cell height above center (Adjusted for goal.jpg)
const LABEL_VERTICAL_FACTOR: float = 0.30 # Percentage of cell height below center (Adjusted for goal.jpg)

# --- Node References ---
var mesh_instance: MeshInstance3D = null
var dots_parent: Node3D = null # Node to hold all dot meshes
var labels_parent: Node3D = null # Node to hold all label nodes

func _ready() -> void:
	generate_grid_mesh()
	generate_dots()
	generate_labels()

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

	# Pre-create materials (optimization)
	var red_material: StandardMaterial3D = StandardMaterial3D.new()
	red_material.albedo_color = dot_color_red
	red_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED

	var blue_material: StandardMaterial3D = StandardMaterial3D.new()
	blue_material.albedo_color = dot_color_blue
	blue_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED

	# Iterate through rows and columns to place dot pairs
	for row in range(grid_rows):
		for col in range(grid_cols):
			# --- Calculate Radius for this cell ---
			var current_radius: float = start_radius + (row * grid_cols + col) * radius_increment

			# --- Create SphereMesh for this cell's radius ---
			# Mesh needs to be created per cell as radius changes
			var cell_sphere_mesh: SphereMesh = SphereMesh.new()
			cell_sphere_mesh.radius = current_radius
			cell_sphere_mesh.height = current_radius * 2.0
			cell_sphere_mesh.radial_segments = 128 # Increase horizontal smoothness
			cell_sphere_mesh.rings = 64 # Increase vertical smoothness

			# --- Calculate Positions ---
			var cell_base_center_x: float = start_x + col * step_x
			var cell_base_center_y: float = start_y + row * step_y
			
			# Calculate minimum offset needed based on radius, adding a small gap
			var small_gap = 0.01 # Adjust this value if needed
			var min_radius_offset: float = current_radius + small_gap
			
			# Calculate desired offset based on cell width and separation factor
			var desired_cell_offset: float = (step_x * dot_separation_factor) / 2.0
			
			# Use the larger of the two offsets to ensure separation
			var horizontal_offset: float = max(min_radius_offset, desired_cell_offset)

			# Calculate vertical offset for dots using constant factor
			var dot_vertical_offset: float = step_y * DOT_VERTICAL_FACTOR
			var dot_y_pos: float = cell_base_center_y + dot_vertical_offset # Add offset to move up

			var z_pos: float = DOT_Z_OFFSET # Use constant

			var blue_pos: Vector3
			var red_pos: Vector3

			# Determine left/right position based on grid pattern
			if (row + col) % 2 == 0:
				# Blue left, Red right
				blue_pos = Vector3(cell_base_center_x - horizontal_offset, dot_y_pos, z_pos)
				red_pos = Vector3(cell_base_center_x + horizontal_offset, dot_y_pos, z_pos)
			else:
				# Red left, Blue right
				red_pos = Vector3(cell_base_center_x - horizontal_offset, dot_y_pos, z_pos)
				blue_pos = Vector3(cell_base_center_x + horizontal_offset, dot_y_pos, z_pos)

			# --- Create Blue Dot Instance ---
			var blue_dot_instance: MeshInstance3D = MeshInstance3D.new()
			blue_dot_instance.mesh = cell_sphere_mesh # Use the mesh for this cell
			blue_dot_instance.material_override = blue_material
			blue_dot_instance.position = blue_pos
			dots_parent.add_child(blue_dot_instance)

			# --- Create Red Dot Instance ---
			var red_dot_instance: MeshInstance3D = MeshInstance3D.new()
			red_dot_instance.mesh = cell_sphere_mesh # Use the same mesh for this cell
			red_dot_instance.material_override = red_material
			red_dot_instance.position = red_pos
			dots_parent.add_child(red_dot_instance)


func generate_labels() -> void:
	# Create or clear parent node for labels
	if labels_parent != null:
		labels_parent.queue_free()
	labels_parent = Node3D.new()
	labels_parent.name = "LabelsContainer"
	add_child(labels_parent)

	# Calculate step sizes (same as grid)
	var step_x: float = grid_size.x / grid_cols
	var step_y: float = grid_size.y / grid_rows

	# Calculate start offset for cell centers (same as dots)
	var start_x: float = -grid_size.x / 2.0 + step_x / 2.0
	var start_y: float = -grid_size.y / 2.0 + step_y / 2.0

	# Iterate through rows and columns to place labels
	for row in range(grid_rows):
		for col in range(grid_cols):
			# Calculate cell base center position (X is same, Y needs adjustment)
			var cell_base_center_x: float = start_x + col * step_x
			var cell_base_center_y: float = start_y + row * step_y # Base Y for calculations

			# Calculate vertical offset for labels using constant factor
			var label_vertical_offset_dynamic: float = step_y * LABEL_VERTICAL_FACTOR
			var label_y_pos: float = cell_base_center_y - label_vertical_offset_dynamic # Subtract offset to move down

			# Position label slightly in front of dots using constant Z offset
			var label_pos: Vector3 = Vector3(cell_base_center_x, label_y_pos, LABEL_Z_OFFSET)

			# --- Calculate Radius for this cell (same as in generate_dots) ---
			var current_radius: float = start_radius + (row * grid_cols + col) * radius_increment

			# Create Label3D node
			var label_instance: Label3D = Label3D.new()

			# Set text to "r = 0.xxx" format
			label_instance.text = "r = %.3f" % current_radius

			# Configure label appearance
			label_instance.font_size = label_font_size
			label_instance.modulate = label_color # Use modulate for color
			label_instance.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			label_instance.vertical_alignment = VERTICAL_ALIGNMENT_CENTER # Align text vertically within its bounds
			label_instance.billboard = BaseMaterial3D.BILLBOARD_ENABLED # Always face camera
			label_instance.no_depth_test = true # Render on top of other objects

			# Set position and add to the container
			label_instance.position = label_pos
			labels_parent.add_child(label_instance)
