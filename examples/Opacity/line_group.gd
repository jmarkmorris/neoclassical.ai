extends Node3D

@export var stroke_width: float = 3.0 # Use float for potential scaling
@export var num_lines: int = 101
@export var line_height: float = 30.0 # Adjusted default
@export var group_width: float = 240.0 # Adjusted default

func _ready():
	print("  LineGroup (Width: %d): _ready() called. Generating mesh..." % stroke_width) # DEBUG
	generate_lines_mesh()

func generate_lines_mesh():
	print("    LineGroup (Width: %d): generate_lines_mesh() called." % stroke_width) # DEBUG
	var mesh = ArrayMesh.new()
	var vertices = PackedVector3Array()
	var colors = PackedColorArray()
	var indices = PackedInt32Array()

	if num_lines <= 1:
		printerr("Cannot draw lines with num_lines <= 1")
		return

	var spacing = group_width / float(num_lines - 1)
	var y_bottom = -line_height / 2.0
	var y_top = line_height / 2.0
	var current_vert_index = 0

	for i in range(num_lines):
		var x_center = i * spacing - group_width / 2.0
		# Scale the stroke width similarly to other dimensions
		var scaled_stroke_width = stroke_width
		# Use scaled_stroke_width for quad dimensions
		var half_width = scaled_stroke_width / 2.0
		var x_left = x_center - half_width
		var x_right = x_center + half_width

		# Calculate opacity (alpha) based on index
		var alpha = i / float(num_lines - 1) # Correct calculation for 0 to 1
		var color = Color(1, 1, 1, alpha)

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
		# Triangle 1: bottom-left, bottom-right, top-right
		indices.append(current_vert_index + 0)
		indices.append(current_vert_index + 1)
		indices.append(current_vert_index + 2)
		# Triangle 2: bottom-left, top-right, top-left
		indices.append(current_vert_index + 0)
		indices.append(current_vert_index + 2)
		indices.append(current_vert_index + 3)

		current_vert_index += 4

	print("    LineGroup (Width: %d): Generated %d vertices, %d indices." % [stroke_width, vertices.size(), indices.size()]) # DEBUG
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
	material.vertex_color_use_as_albedo = true # Enable vertex colors
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED # Unshaded for direct color
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA # Enable transparency
	material.cull_mode = BaseMaterial3D.CULL_DISABLED # Disable culling
	# Optional: Disable culling if lines are very thin and might disappear
	# material.cull_mode = BaseMaterial3D.CULL_DISABLED
	print("    LineGroup (Width: %d): Material created. Shading: %s, Transparency: %s, VertexColorAlbedo: %s" % [stroke_width, material.shading_mode, material.transparency, material.vertex_color_use_as_albedo]) # DEBUG

	mesh_instance.material_override = material # Apply material

	add_child(mesh_instance)
	print("    LineGroup (Width: %d): MeshInstance3D added as child." % stroke_width) # DEBUG
