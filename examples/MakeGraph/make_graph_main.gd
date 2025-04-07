extends Node3D

# Constants for colors matching Manim's colors
const INDIGO: Color = Color(0.294118, 0, 0.509804, 1)
const BLUE: Color = Color(0, 0, 1)
const RED: Color = Color(1, 0, 0)
const GREEN: Color = Color(0, 1, 0)
const YELLOW: Color = Color(1, 1, 0)
const WHITE: Color = Color(1, 1, 1)

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
	camera.position = Vector3(0, 0, 8)  # Zoom in
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
	title_text.font_size = 72
	title_text.modulate = WHITE
	title_text.position = Vector3(0, 5, 0)
	add_child(title_text)
	
	# Create subtitle
	subtitle_text = Label3D.new()
	subtitle_text.text = "axes.plot(lambda x: np.sin(x)) + axes.get_graph_label(graph, label)"
	subtitle_text.font_size = 36
	subtitle_text.modulate = YELLOW
	subtitle_text.position = Vector3(0, 4, 0)
	add_child(subtitle_text)

func create_axes() -> void:
	# Create axes container
	axes = Node3D.new()
	axes.position = Vector3(0, 0, 0)
	add_child(axes)
	
	# Create x-axis
	var x_axis = MeshInstance3D.new()
	var x_mesh = ImmediateMesh.new()
	x_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
	x_mesh.surface_add_vertex(Vector3(-10, 0, 0))
	x_mesh.surface_add_vertex(Vector3(10, 0, 0))
	x_mesh.surface_end()
	x_axis.mesh = x_mesh
	
	var x_material = StandardMaterial3D.new()
	x_material.albedo_color = GREEN
	x_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	x_axis.material_override = x_material
	axes.add_child(x_axis)
	
	# Create y-axis
	var y_axis = MeshInstance3D.new()
	var y_mesh = ImmediateMesh.new()
	y_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
	y_mesh.surface_add_vertex(Vector3(0, -1.5, 0))
	y_mesh.surface_add_vertex(Vector3(0, 1.5, 0))
	y_mesh.surface_end()
	y_axis.mesh = y_mesh
	
	var y_material = StandardMaterial3D.new()
	y_material.albedo_color = GREEN
	y_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	y_axis.material_override = y_material
	axes.add_child(y_axis)
	
	# Create x-axis ticks
	create_x_ticks()
	
	# Create y-axis ticks
	create_y_ticks()
	
	# Create axis labels
	var x_label = Label3D.new()
	x_label.text = "x"
	x_label.font_size = 48
	x_label.modulate = WHITE
	x_label.position = Vector3(10.5, 0, 0)
	axes.add_child(x_label)
	
	var y_label = Label3D.new()
	y_label.text = "y"
	y_label.font_size = 48
	y_label.modulate = WHITE
	y_label.position = Vector3(0, 2, 0)
	axes.add_child(y_label)

func create_x_ticks() -> void:
	# Create x-axis ticks and numbers
	for i in range(-10, 11, 2):
		# Create tick
		var tick = MeshInstance3D.new()
		var tick_mesh = ImmediateMesh.new()
		tick_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
		tick_mesh.surface_add_vertex(Vector3(i, -0.1, 0))
		tick_mesh.surface_add_vertex(Vector3(i, 0.1, 0))
		tick_mesh.surface_end()
		tick.mesh = tick_mesh
		
		var tick_material = StandardMaterial3D.new()
		tick_material.albedo_color = GREEN
		tick_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		tick.material_override = tick_material
		axes.add_child(tick)
		
		# Create number label
		var number = Label3D.new()
		number.text = str(i)
		number.font_size = 32
		number.modulate = WHITE
		number.position = Vector3(i, -0.3, 0)
		axes.add_child(number)

func create_y_ticks() -> void:
	# Create y-axis ticks and numbers
	for i in range(-1, 2):
		# Create tick
		var tick = MeshInstance3D.new()
		var tick_mesh = ImmediateMesh.new()
		tick_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
		tick_mesh.surface_add_vertex(Vector3(-0.1, i, 0))
		tick_mesh.surface_add_vertex(Vector3(0.1, i, 0))
		tick_mesh.surface_end()
		tick.mesh = tick_mesh
		
		var tick_material = StandardMaterial3D.new()
		tick_material.albedo_color = GREEN
		tick_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		tick.material_override = tick_material
		axes.add_child(tick)
		
		# Create number label if not at origin
		if i != 0:
			var number = Label3D.new()
			number.text = str(i)
			number.font_size = 32
			number.modulate = WHITE
			number.position = Vector3(-0.3, i, 0)
			axes.add_child(number)

func create_graphs() -> void:
	# Create sin graph
	sin_graph = MeshInstance3D.new()
	var sin_mesh = ImmediateMesh.new()
	sin_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	
	# Generate points for sin curve
	for x in range(-1000, 1001):
		var x_val = x * 0.01
		var y_val = sin(x_val)
		sin_mesh.surface_add_vertex(Vector3(x_val, y_val, 0))
	
	sin_mesh.surface_end()
	sin_graph.mesh = sin_mesh
	
	var sin_material = StandardMaterial3D.new()
	sin_material.albedo_color = BLUE
	sin_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sin_graph.material_override = sin_material
	axes.add_child(sin_graph)
	
	# Create cos graph
	cos_graph = MeshInstance3D.new()
	var cos_mesh = ImmediateMesh.new()
	cos_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP)
	
	# Generate points for cos curve
	for x in range(-1000, 1001):
		var x_val = x * 0.01
		var y_val = cos(x_val)
		cos_mesh.surface_add_vertex(Vector3(x_val, y_val, 0))
	
	cos_mesh.surface_end()
	cos_graph.mesh = cos_mesh
	
	var cos_material = StandardMaterial3D.new()
	cos_material.albedo_color = RED
	cos_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	cos_graph.material_override = cos_material
	axes.add_child(cos_graph)

func create_vertical_line() -> void:
	# Create vertical line at x=2π
	vert_line = MeshInstance3D.new()
	var line_mesh = ImmediateMesh.new()
	line_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
	line_mesh.surface_add_vertex(Vector3(TAU, -1.5, 0))
	line_mesh.surface_add_vertex(Vector3(TAU, 1.5, 0))
	line_mesh.surface_end()
	vert_line.mesh = line_mesh
	
	var line_material = StandardMaterial3D.new()
	line_material.albedo_color = YELLOW
	line_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	vert_line.material_override = line_material
	axes.add_child(vert_line)

func create_labels() -> void:
	# Create sin label
	var sin_label = Label3D.new()
	sin_label.text = "sin(x)"
	sin_label.font_size = 40
	sin_label.modulate = BLUE
	sin_label.position = Vector3(-8, -1, 0)
	axes.add_child(sin_label)
	
	# Create cos label
	var cos_label = Label3D.new()
	cos_label.text = "cos(x)"
	cos_label.font_size = 40
	cos_label.modulate = RED
	cos_label.position = Vector3(8, -1, 0)
	axes.add_child(cos_label)
	
	# Create vertical line label
	var line_label = Label3D.new()
	line_label.text = "x = 2π"
	line_label.font_size = 40
	line_label.modulate = WHITE
	line_label.position = Vector3(TAU + 0.5, 1, 0)
	axes.add_child(line_label)
