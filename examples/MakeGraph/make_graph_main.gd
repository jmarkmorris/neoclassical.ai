extends Node3D

# Constants for colors matching Manim's colors
const INDIGO: Color = Color(0.294118, 0, 0.509804, 1)
const BLUE: Color = Color(0, 0, 1)
const RED: Color = Color(1, 0, 0)
const GREEN: Color = Color(0, 1, 0)
const YELLOW: Color = Color(1, 1, 0)
const WHITE: Color = Color(1, 1, 1)
const SEAFOAM_GREEN: Color = Color(0.596, 0.984, 0.596, 1)

const LINE_THICKNESS: float = 0.06 # Reduced thickness

# References to key nodes
var axes: Node3D
var sin_graph: MeshInstance3D
var cos_graph: MeshInstance3D
var vert_line: MeshInstance3D
var title_text: Label3D
var subtitle_text: Label3D

func _ready() -> void:
	# Setup environment
	setup_environment()
	
	# Create title and subtitle
	create_title()
	
	# Create axes and graphs
	create_axes()
	create_graphs()
	
	# Create vertical line at x=2π
	create_vertical_line()
	
	# Create labels
	create_labels()

func setup_environment() -> void:
	# Add camera
	var camera = Camera3D.new()
	camera.position = Vector3(0, 0, 10) # Zoomed in a bit more
	camera.look_at(Vector3.ZERO)
	add_child(camera)
	
	# Set background color
	var environment: WorldEnvironment = WorldEnvironment.new()
	var environment_settings: Environment = Environment.new()
	environment_settings.background_mode = Environment.BG_COLOR
	environment_settings.background_color = INDIGO
	environment.environment = environment_settings
	add_child(environment)

	# Add lighting
	var light = DirectionalLight3D.new()
	light.position = Vector3(10, 10, 10)
	light.look_at(Vector3.ZERO)
	add_child(light)

func create_title() -> void:
	# Create title
	title_text = Label3D.new()
	title_text.text = "Function Graphing Example"
	title_text.font_size = 144
	title_text.modulate = WHITE
	title_text.position = Vector3(0, 6.5, 0)
	add_child(title_text)
	
	# Create subtitle
	subtitle_text = Label3D.new()
	subtitle_text.text = "axes.plot(lambda x: np.sin(x)) + axes.get_graph_label(graph, label)"
	subtitle_text.font_size = 64
	subtitle_text.modulate = YELLOW
	subtitle_text.position = Vector3(0, 5.5, 0)
	add_child(subtitle_text)

func create_axes() -> void:
	# Create axes container
	axes = Node3D.new()
	axes.position = Vector3(0, 0, 0)
	add_child(axes)

	# Define axis limits
	var x_min = -10.0
	var x_max = 10.0
	var y_min = -1.5
	var y_max = 1.5

	# Create thick x-axis
	var x_axis_mesh_instance = create_thick_line_mesh(Vector3(x_min, 0, 0), Vector3(x_max, 0, 0), LINE_THICKNESS, SEAFOAM_GREEN)
	axes.add_child(x_axis_mesh_instance)

	# Create thick y-axis
	var y_axis_mesh_instance = create_thick_line_mesh(Vector3(0, y_min, 0), Vector3(0, y_max, 0), LINE_THICKNESS, SEAFOAM_GREEN)
	axes.add_child(y_axis_mesh_instance)

	# Create x-axis ticks
	create_x_ticks()
	
	# Create y-axis ticks
	create_y_ticks()
	
	# Create axis labels
	var x_label = Label3D.new()
	x_label.text = "x"
	x_label.font_size = 64 # Increased size
	x_label.modulate = WHITE
	x_label.position = Vector3(10.5, -0.3, 0) # Adjusted position
	axes.add_child(x_label)
	
	var y_label = Label3D.new()
	y_label.text = "y"
	y_label.font_size = 64 # Increased size
	y_label.modulate = WHITE
	y_label.position = Vector3(0.3, 1.8, 0) # Adjusted position
	axes.add_child(y_label)

func create_x_ticks() -> void:
	# Create x-axis ticks and numbers
	var tick_height = 0.2 # Total height of the tick mark
	var tick_thickness = LINE_THICKNESS * 0.7 # Make ticks slightly thinner than axes

	for i in range(-10, 11, 2):
		# Create tick
		var tick_start = Vector3(i, -tick_height / 2.0, 0)
		var tick_end = Vector3(i, tick_height / 2.0, 0)
		var tick = create_thick_line_mesh(tick_start, tick_end, tick_thickness, SEAFOAM_GREEN)
		axes.add_child(tick)

		# Create number label
		var number = Label3D.new()
		number.text = str(i)
		number.font_size = 48 # Increased size
		number.modulate = WHITE
		number.position = Vector3(i, -0.5, 0) # Moved lower
		axes.add_child(number)

func create_y_ticks() -> void:
	# Create y-axis ticks and numbers
	var tick_width = 0.2 # Total width of the tick mark
	var tick_thickness = LINE_THICKNESS * 0.7 # Make ticks slightly thinner than axes

	for i in range(-1, 2):
		# Create tick
		var tick_start = Vector3(-tick_width / 2.0, i, 0)
		var tick_end = Vector3(tick_width / 2.0, i, 0)
		var tick = create_thick_line_mesh(tick_start, tick_end, tick_thickness, SEAFOAM_GREEN)
		axes.add_child(tick)

		# Create number label if not at origin
		if i != 0:
			var number = Label3D.new()
			number.text = str(i)
			number.font_size = 48 # Increased size
			number.modulate = WHITE
			number.position = Vector3(-0.6, i, 0) # Moved further left
			axes.add_child(number)

func create_graphs() -> void:
	# Generate points for sin curve
	var sin_points: Array[Vector3] = []
	# Generate points for sin curve
	for x in range(-1000, 1001):
		var x_val = x * 0.01
		var y_val = sin(x_val)
		sin_points.append(Vector3(x_val, y_val, 0))

	# Create thick sin graph using the helper function
	sin_graph = create_thick_curve_mesh(sin_points, LINE_THICKNESS, BLUE)
	axes.add_child(sin_graph)

	# Generate points for cos curve
	var cos_points: Array[Vector3] = []
	# Generate points for cos curve
	for x in range(-1000, 1001):
		var x_val = x * 0.01
		var y_val = cos(x_val)
		cos_points.append(Vector3(x_val, y_val, 0))

	# Create thick cos graph using the helper function
	cos_graph = create_thick_curve_mesh(cos_points, LINE_THICKNESS, RED)
	axes.add_child(cos_graph)

func create_vertical_line() -> void:
	# Create vertical line at x=2π
	var y_min = -1.5 # Use the same limits as the y-axis
	var y_max = 1.5
	var x_pos = TAU # Constant x position (2 * PI)

	var line_start = Vector3(x_pos, y_min, 0)
	var line_end = Vector3(x_pos, y_max, 0)

	# Create thick vertical line using the helper function
	vert_line = create_thick_line_mesh(line_start, line_end, LINE_THICKNESS, YELLOW)
	axes.add_child(vert_line)

func create_labels() -> void:
	# Create sin label
	var sin_label = Label3D.new()
	sin_label.text = "sin(x)"
	sin_label.font_size = 64 # Increased size
	sin_label.modulate = BLUE
	sin_label.position = Vector3(-9.5, 0.8, 0) # Adjusted position
	axes.add_child(sin_label)
	
	# Create cos label
	var cos_label = Label3D.new()
	cos_label.text = "cos(x)"
	cos_label.font_size = 64 # Increased size
	cos_label.modulate = RED
	cos_label.position = Vector3(9.5, -0.8, 0) # Adjusted position
	axes.add_child(cos_label)
	
	# Create vertical line label
	var line_label = Label3D.new()
	line_label.text = "x = 2π"
	line_label.font_size = 64 # Increased size
	line_label.modulate = WHITE
	line_label.position = Vector3(TAU, 1.8, 0) # Centered above line
	axes.add_child(line_label)

# Helper function to create a thick line mesh using TRIANGLE_STRIP
func create_thick_line_mesh(start_point: Vector3, end_point: Vector3, thickness: float, color: Color) -> MeshInstance3D:
	var mesh_instance = MeshInstance3D.new()
	var mesh = ImmediateMesh.new()
	
	var dir = (end_point - start_point).normalized()
	# Perpendicular vector in the XY plane (assuming Z=0 for 2D drawing)
	var perp = Vector3(-dir.y, dir.x, 0) 
	var offset = perp * thickness / 2.0
	
	# Calculate the four corners of the rectangle representing the thick line
	var v1 = start_point - offset # Bottom-left (relative to line direction)
	var v2 = start_point + offset # Top-left
	var v3 = end_point - offset   # Bottom-right
	var v4 = end_point + offset   # Top-right
	
	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	
	# Add vertices in triangle strip order (v1, v2, v3, v4 makes a quad)
	mesh.surface_add_vertex(v1)
	mesh.surface_add_vertex(v2)
	mesh.surface_add_vertex(v3)
	mesh.surface_add_vertex(v4)
	
	mesh.surface_end()
	
	mesh_instance.mesh = mesh
	
	# Use an unshaded material so the color is exact
	var material = StandardMaterial3D.new()
	material.albedo_color = color
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mesh_instance.material_override = material
	
	return mesh_instance

# Helper function to create a thick curve mesh using TRIANGLE_STRIP
# Takes an array of points defining the curve path.
func create_thick_curve_mesh(points: Array[Vector3], thickness: float, color: Color) -> MeshInstance3D:
	var mesh_instance = MeshInstance3D.new()
	var mesh = ImmediateMesh.new()
	
	if points.size() < 2:
		printerr("Need at least 2 points for a thick curve.")
		return mesh_instance # Return empty mesh instance

	mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	
	var half_thickness = thickness / 2.0
	
	# Iterate through each point to generate vertices for the strip
	for i in range(points.size()):
		var current_point = points[i]
		var tangent: Vector3
		
		# Calculate tangent vector at the current point
		if i == 0:
			# First point: tangent is direction to the next point
			tangent = (points[i+1] - current_point).normalized()
		elif i == points.size() - 1:
			# Last point: tangent is direction from the previous point
			tangent = (current_point - points[i-1]).normalized()
		else:
			# Intermediate point: tangent is the average direction 
			# from the previous point and to the next point. This helps smooth corners.
			var dir_from_prev = (current_point - points[i-1]).normalized()
			var dir_to_next = (points[i+1] - current_point).normalized()
			tangent = (dir_from_prev + dir_to_next).normalized()
			# Handle potential zero vector if directions cancel (e.g., sharp 180 turn)
			if tangent.length_squared() < 0.0001:
				tangent = (points[i+1] - current_point).normalized() # Fallback

		# Calculate the normal vector (perpendicular to tangent in XY plane)
		var normal = Vector3(-tangent.y, tangent.x, 0)
		
		# Calculate the two vertices for the strip at this point (left and right)
		var v_left = current_point - normal * half_thickness
		var v_right = current_point + normal * half_thickness
		
		# Add the pair of vertices to the strip. 
		# The strip connects (left[i], right[i], left[i+1], right[i+1]) to form quads.
		mesh.surface_add_vertex(v_left)
		mesh.surface_add_vertex(v_right)

	mesh.surface_end()
	
	mesh_instance.mesh = mesh
	
	# Use an unshaded material so the color is exact
	var material = StandardMaterial3D.new()
	material.albedo_color = color
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mesh_instance.material_override = material
	
	return mesh_instance
