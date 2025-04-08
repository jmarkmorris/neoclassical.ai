extends Node3D

@export var start_radius: float = 0.002
@export var radius_increment: float = 0.002
@export var num_cols: int = 14
@export var num_rows: int = 8
@export var cell_size: Vector3 = Vector3(0.2, 0.01, 0.2)
@export var circle_spacing: float = 0.07
@export var label_offset: float = 0.1

var circle_scene = preload("res://examples/CircleSizes/Circle.tscn")
var default_env = preload("res://examples/CircleSizes/default_env.tres")
var background_color = Color(0.18, 0.09, 0.31) # Dark indigo/purple

func _ready():
	# Set up environment
	var environment = WorldEnvironment.new()
	if ResourceLoader.exists("res://examples/CircleSizes/default_env.tres"):
		environment.environment = default_env
	else:
		var env = Environment.new()
		env.background_mode = Environment.BG_COLOR
		env.background_color = background_color
		environment.environment = env
	add_child(environment)
	
	# Set up camera
	var camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 3.0
	camera.position = Vector3(0, 2, 0)
	camera.rotation_degrees = Vector3(-90, 0, 0)
	add_child(camera)
	
	# Add lighting
	var light = DirectionalLight3D.new()
	light.position = Vector3(0, 5, 0)
	light.rotation_degrees = Vector3(-90, 0, 0)
	light.light_energy = 1.2
	add_child(light)
	
	create_grid()

func create_grid():
	for row in range(num_rows):
		for col in range(num_cols):
			var radius = start_radius + (row * num_cols + col) * radius_increment
			create_cell(col, row, radius)

func create_cell(col: int, row: int, radius: float):
	var cell = Node3D.new()
	add_child(cell)
	
	# Position the cell
	cell.position = Vector3(
		(col - num_cols/2 + 0.5) * cell_size.x,
		0,
		(row - num_rows/2 + 0.5) * cell_size.z
	)
	
	# Create blue circle
	var blue_circle = circle_scene.instantiate()
	blue_circle.position = Vector3(-circle_spacing/2, 0, 0)
	blue_circle.set_circle_properties(radius, Color(0, 0, 1)) # Blue
	cell.add_child(blue_circle)
	
	# Create red circle
	var red_circle = circle_scene.instantiate()
	red_circle.position = Vector3(circle_spacing/2, 0, 0)
	red_circle.set_circle_properties(radius, Color(1, 0, 0)) # Red
	cell.add_child(red_circle)
	
	# Create radius label using Label3D
	var label = Label3D.new()
	label.text = "r = %.3f" % radius
	label.font_size = 16
	label.position = Vector3(0, 0, label_offset)
	label.rotation_degrees = Vector3(-90, 0, 0)  # Make it face the camera
	label.modulate = Color.WHITE
	cell.add_child(label)
