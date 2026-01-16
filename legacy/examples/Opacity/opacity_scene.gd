extends Node3D

# Preload helper scripts
const LineGroup = preload("res://line_group.gd")
const AxisDisplay = preload("res://axis_display.gd")

# Configuration constants (adjust as needed for visual match)
const VIEWPORT_WIDTH_APPROX = 1280 # Approximate target width for positioning
const VIEWPORT_HEIGHT_APPROX = 720 # Approximate target height for positioning
const CAMERA_SIZE = 200 # Orthogonal camera size (adjust to fit content)
const TITLE_FONT_SIZE = 40 # Adjust for Label3D
const SUBTITLE_FONT_SIZE = 28 # Adjust for Label3D
const WIDTH_LABEL_FONT_SIZE = 32 # Adjust for Label3D
const PERCENT_LABEL_FONT_SIZE = 28 # Adjust for Label3D
const LABEL_PIXEL_SIZE = 0.1 # Increased significantly (was 0.01)

const GROUP_WIDTH = 800.0 * 0.3 # Scale down 3D size
const GROUP_HEIGHT = 100.0 * 0.3 # Scale down 3D size
const VERTICAL_SPACING = 50.0 * 0.3 # Scale down 3D size
const WIDTH_LABEL_PADDING = 20.0 * 0.3 # Scale down 3D size
const AXIS_TICK_LABEL_OFFSET_Y = 10.0 * 0.3 # Scale down 3D size
const AXIS_DISPLAY_OFFSET_Y = 20.0 * 0.3 # Scale down 3D size

const TOP_MARGIN = (50.0 + 36.0) * 0.3 # Scale down 3D size
const TITLE_SUBTITLE_SPACING = 10.0 * 0.3 # Scale down 3D size
const SUBTITLE_GROUP_SPACING = 50.0 * 0.3 # Scale down 3D size


func _ready():
	print("--- opacity_scene.gd: _ready() started ---") # DEBUG START
	# --- Camera Setup ---
	var camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = CAMERA_SIZE
	# Position camera to view the XY plane (Z=0)
	camera.position = Vector3(0, 0, CAMERA_SIZE * 1.5) # Adjust Z based on near/far clip if needed
	camera.look_at(Vector3.ZERO, Vector3.UP)
	add_child(camera)
	print("Camera3D added. Global Position: %s, Size: %s, Projection: %s" % [camera.global_position, camera.size, camera.projection]) # DEBUG
	print("Camera3D: near = %s, far = %s" % [camera.near, camera.far]) # DEBUG

	# --- Add WorldEnvironment ---
	var world_env = WorldEnvironment.new()
	var env = Environment.new()
	# Use a color background mode to match the project settings
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.294118, 0, 0.509804, 1)
	world_env.environment = env
	add_child(world_env)
	print("  WorldEnvironment added.") # DEBUG
	# --- End WorldEnvironment ---

	# --- DEBUG: Remove test cube ---
	#var test_cube_mesh = BoxMesh.new()
	#var test_cube_mat = StandardMaterial3D.new()
	#test_cube_mat.albedo_color = Color.BLUE
	#var test_cube = MeshInstance3D.new()
	#test_cube.mesh = test_cube_mesh
	#test_cube.material_override = test_cube_mat
	#test_cube.position = Vector3.ZERO # Place at origin
	#test_cube.scale = Vector3(20, 20, 20) # Make it reasonably large
	#add_child(test_cube)
	#print("  DEBUG Test Cube added. Global Position: %s, Scale: %s" % [test_cube.global_position, test_cube.scale]) # DEBUG
	# --- END DEBUG ---

	# --- UI Elements (using Label3D) ---
	# Calculate approximate center based on constants
	var center_x = 0.0 # We center content around origin
	var current_y = VIEWPORT_HEIGHT_APPROX / 2.0 * 0.3 - TOP_MARGIN # Start from top (scaled)

	# Create title label
	var title_label = Label3D.new()
	title_label.text = "Line Opacity Visualization (Even % from 0% to 100%)"
	title_label.font_size = TITLE_FONT_SIZE
	title_label.pixel_size = LABEL_PIXEL_SIZE
	title_label.set_horizontal_alignment(HORIZONTAL_ALIGNMENT_CENTER)
	# Position centered horizontally, at current_y
	title_label.position = Vector3(center_x, current_y, 0)
	add_child(title_label)
	print("Title Label3D added. Global Position: %s" % title_label.global_position) # DEBUG
	current_y -= (TITLE_FONT_SIZE * LABEL_PIXEL_SIZE * 1.5) # Approximate height + spacing

	# Create subtitle label
	var subtitle_label = Label3D.new()
	subtitle_label.text = "drawLine(from, to, color, width)"
	subtitle_label.font_size = SUBTITLE_FONT_SIZE
	subtitle_label.pixel_size = LABEL_PIXEL_SIZE
	subtitle_label.modulate = Color.YELLOW
	subtitle_label.set_horizontal_alignment(HORIZONTAL_ALIGNMENT_CENTER)
	subtitle_label.position = Vector3(center_x, current_y, 0)
	add_child(subtitle_label)
	print("Subtitle Label3D added. Position: %s" % subtitle_label.global_position) # DEBUG
	current_y -= (SUBTITLE_FONT_SIZE * LABEL_PIXEL_SIZE * 1.5) + SUBTITLE_GROUP_SPACING # Approximate height + spacing

	# --- Line Groups ---
	var line_group_widths = [2, 1.5, 1]
	var group_nodes = [] # To store group nodes for later reference if needed

	for i in range(line_group_widths.size()):
		var width = line_group_widths[i]
		
		# Create Line Group Node
		var group = LineGroup.new()
		group.stroke_width = width # This will be used for quad generation
		group.line_height = GROUP_HEIGHT
		group.group_width = GROUP_WIDTH
		group.position = Vector3(center_x, current_y - GROUP_HEIGHT / 2.0, 0) # Center vertically
		add_child(group)
		print("LineGroup (Width: %s) added. Position: %s" % [str(width), group.global_position]) # DEBUG
		group_nodes.append(group)

		# Create Width Label (Child of Group)
		var label_width = Label3D.new()
		label_width.text = "Width: %s" % str(width)
		label_width.font_size = WIDTH_LABEL_FONT_SIZE
		label_width.pixel_size = LABEL_PIXEL_SIZE
		label_width.set_horizontal_alignment(HORIZONTAL_ALIGNMENT_RIGHT)
		label_width.set_vertical_alignment(VERTICAL_ALIGNMENT_CENTER)
		# Position relative to the group's origin (left side, centered vertically)
		var label_x_pos = -GROUP_WIDTH / 2.0 - WIDTH_LABEL_PADDING
		label_width.position = Vector3(label_x_pos, 0, 0.1) # Slightly in front
		group.add_child(label_width) # Add as child
		print("  Width Label3D added to Group %d. Relative Position: %s" % [width, label_width.position]) # DEBUG

		# Update Y for next group
		current_y -= (GROUP_HEIGHT + VERTICAL_SPACING)

	# --- Axis Display ---
	var axis_display = AxisDisplay.new()
	axis_display.group_width = GROUP_WIDTH
	# Position below the last group
	axis_display.position = Vector3(center_x, current_y, 0)
	add_child(axis_display)
	print("AxisDisplay added. Position: %s" % axis_display.global_position) # DEBUG

	# --- Percentage Labels (Children of Axis Display) ---
	var percentages = ["0%", "25%", "50%", "75%", "100%"]
	var num_ticks = percentages.size()
	for i in range(num_ticks):
		var percent_label = Label3D.new()
		percent_label.text = percentages[i]
		percent_label.font_size = PERCENT_LABEL_FONT_SIZE
		percent_label.pixel_size = LABEL_PIXEL_SIZE
		percent_label.set_horizontal_alignment(HORIZONTAL_ALIGNMENT_CENTER)
		percent_label.set_vertical_alignment(VERTICAL_ALIGNMENT_TOP) # Align top below tick

		# Calculate X position relative to axis_display origin
		var tick_x_pos = (i / float(num_ticks - 1)) * GROUP_WIDTH - GROUP_WIDTH / 2.0
		# Position below the tick, centered horizontally
		percent_label.position = Vector3(tick_x_pos, -axis_display.tick_height - AXIS_TICK_LABEL_OFFSET_Y, 0.1) # Slightly in front
		axis_display.add_child(percent_label) # Add as child
		print("  Percent Label3D '%s' added to AxisDisplay. Relative Position: %s" % [percent_label.text, percent_label.position]) # DEBUG
	print("--- opacity_scene.gd: _ready() finished ---") #DEBUG END
