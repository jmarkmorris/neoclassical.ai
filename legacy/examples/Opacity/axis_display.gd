extends Node3D

@export var num_ticks: int = 5
@export var tick_height: float = 10.0 * 0.3 # Scale down
@export var tick_width: float = 3.0 * 0.3 # Scale down
@export var group_width: float = 800.0 * 0.3 # Scale down (must match LineGroup)

func _ready():
	print("AxisDisplay: _ready() called. Generating mesh...") # DEBUG
	generate_ticks_mesh()

func generate_ticks_mesh():
	print("  AxisDisplay: generate_ticks_mesh() called.") # DEBUG
	var mesh = ArrayMesh.new()
	var vertices = PackedVector3Array()
	var colors = PackedColorArray()
	var indices = PackedInt32Array()

	if num_ticks <= 1:
		printerr("Cannot draw ticks with num_ticks <= 1")
		return

	var spacing = group_width / float(num_ticks - 1)
	var y_bottom = -tick_height / 2.0 # Center vertically around origin
	var y_top = tick_height / 2.0
	var current_vert_index = 0
	var color = Color(1, 1, 1, 1) # Ticks are fully opaque white

	for i in range(num_ticks):
		var x_center = i * spacing - group_width / 2.0 # Center horizontally
		var half_width = tick_width / 2.0
		var x_left = x_center - half_width
		var x_right = x_center + half_width

		# Define 4 vertices for the quad (Z=0)
		vertices.append(Vector3(x_left, y_bottom, 0))
		vertices.append(Vector3(x_right, y_bottom, 0))
		vertices.append(Vector3(x_right, y_top, 0))
		vertices.append(Vector3(x_left, y_top, 0))

		# Add color for each vertex
		colors.append(color)
		colors.append(color)
		colors.append(color)
		colors.append(color)

		# Add indices for two triangles forming the quad
		indices.append(current_vert_index + 0)
		indices.append(current_vert_index + 1)
		indices.append(current_vert_index + 2)
		indices.append(current_vert_index + 0)
		indices.append(current_vert_index + 2)
		indices.append(current_vert_index + 3)

		current_vert_index += 4

	print("  AxisDisplay: Generated %d vertices, %d indices." % [vertices.size(), indices.size()]) # DEBUG
	# Assemble mesh arrays
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_COLOR] = colors
	arrays[Mesh.ARRAY_INDEX] = indices

	# Add surface
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)

	# Create MeshInstance
	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = mesh

	# Create Material
	var material = StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	# Ticks are opaque, but keep alpha for consistency if needed later
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	print("  AxisDisplay: Material created. Shading: %s, Transparency: %s, VertexColorAlbedo: %s" % [material.shading_mode, material.transparency, material.vertex_color_use_as_albedo]) # DEBUG

	mesh_instance.material_override = material # Apply material

	add_child(mesh_instance)
	print("  AxisDisplay: MeshInstance3D added as child.") # DEBUG
