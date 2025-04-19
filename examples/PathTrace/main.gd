extends Node3D

# --- Constants ---

# Define Colors
const INDIGO: Color = Color("#4B0082")
const PURE_BLUE: Color = Color("#0000FF")
const PURE_RED: Color = Color("#FF0000")
const LIGHT_BLUE: Color = Color("#ADD8E6") # Or BLUE_C from Manim: Color("#58C4DD")
const LIGHT_RED: Color = Color("#FFC0CB")  # Or RED_C from Manim: Color("#FC6255")

# Particle Properties
const PARTICLE_RADIUS: float = 0.1 # Adjusted from Manim's 0.075 for visibility
const NUM_PARTICLES_PER_COLOR: int = 3

# Particle Configurations (Object Color, Trail Color)
const PARTICLE_CONFIGS: Array[Dictionary] = [
	{"object_color": PURE_BLUE, "trail_color": LIGHT_BLUE},
	{"object_color": PURE_BLUE, "trail_color": LIGHT_BLUE},
	{"object_color": PURE_BLUE, "trail_color": LIGHT_BLUE},
	{"object_color": PURE_RED, "trail_color": LIGHT_RED},
	{"object_color": PURE_RED, "trail_color": LIGHT_RED},
	{"object_color": PURE_RED, "trail_color": LIGHT_RED}
]

# Screen Boundaries (adjust as needed based on camera view) - Moved Up 15%
const BOUNDS_X_MIN: float = -14.0
const BOUNDS_X_MAX: float = 14.0
const BOUNDS_Y_MIN: float = -9.875 # -12.5 + 2.625
const BOUNDS_Y_MAX: float = 7.625  # 5.0 + 2.625 # Keep bounds for initial placement/containment? Or remove? Let's keep for now.

# Physics Parameters
const INITIAL_POS_SPREAD: float = 2.0 # Spread for initial random positions around center
const INITIAL_VEL_MAGNITUDE: float = 1.0 # Initial speed magnitude for particles
const SPEED_OF_POTENTIAL: float = 1.0 # Speed at which interaction propagates (set equal to initial speed as requested)
const COULOMB_CONSTANT: float = 5.0 # Strength of attraction/repulsion force
const MIN_DISTANCE_SQ: float = 0.01 # Minimum distance squared to prevent division by zero/huge forces
const PARTICLE_MASS: float = 1.0 # Mass of particles (affects acceleration)
const MAX_HISTORY_SECONDS: float = 5.0 # How many seconds of position history to store
const HISTORY_POINTS_PER_SECOND: int = 30 # How many points per second to store in history

# Boundary Constraint Constants
const BOUNDARY_SOFTNESS: float = 2.0  # Controls the "elasticity" of boundary constraints
const BOUNDARY_FORCE_MULTIPLIER: float = 15.0  # Scales the magnitude of boundary push-back forces
const BOUNDARY_INNER_MARGIN: float = 1.0  # Distance from boundary where soft constraint begins


# --- Scene Variables ---
# var path_followers: Array[PathFollow3D] = [] # No longer needed
var trail_mesh_instances: Array[MeshInstance3D] = [] # Nodes to hold the trail meshes
var trail_meshes: Array[ImmediateMesh] = []   # The actual ImmediateMesh resources
var trail_materials: Array[StandardMaterial3D] = [] # To store trail materials
var trail_points: Array[PackedVector3Array] = [] # To store points for each trail
var particle_meshes: Array[MeshInstance3D] = [] # To easily access particle positions

# Particle Path State
var particle_paths: Array[Array] = [] # Array of predefined paths for each particle
var particle_velocities: Array[Vector3] = [] # Velocities for each particle
var particle_charges: Array[float] = [] # Charges for each particle
var particle_histories: Array[Array] = [] # History of particle positions

var current_time: float = 0.0 # Keep track of animation time


# --- Scene Setup ---

# Generate a random path for a particle
func _generate_particle_path(start_pos: Vector3) -> Array:
	var path: Array = [start_pos]
	var current_pos = start_pos
	
	# Dynamically generate path points (fewer points initially, will be expanded by smoothing)
	while path.size() < 32:
		# Use a smaller step size for more controlled randomness
		var angle = randf() * TAU # Random angle between 0 and 2π
		var step_size = randf_range(0.5, 2.0)
		var next_pos = current_pos + Vector3(cos(angle), sin(angle), 0) * step_size
		
		# Check boundary constraints with margin to avoid edge cases
		if (next_pos.x >= BOUNDS_X_MIN + 1.0 and next_pos.x <= BOUNDS_X_MAX - 1.0 and 
			next_pos.y >= BOUNDS_Y_MIN + 1.0 and next_pos.y <= BOUNDS_Y_MAX - 1.0):
			path.append(next_pos)
			current_pos = next_pos
		
		# Prevent infinite loop if boundaries are too restrictive
		if path.size() > 1000:
			break
	
	# Apply Bézier curve smoothing
	return _smooth_path_with_bezier(path)

# Smooth a path using quadratic Bézier curves
func _smooth_path_with_bezier(original_path: Array) -> Array:
	if original_path.size() < 3:
		return original_path  # Not enough points to smooth
	
	var smoothed_path: Array = []
	var segments_per_curve = 10  # More segments = smoother curve
	
	# Start with the first point
	smoothed_path.append(original_path[0])
	
	# Process each set of three points to create a quadratic Bézier curve
	for i in range(original_path.size() - 2):
		var p0 = original_path[i]
		var p1 = original_path[i + 1]
		var p2 = original_path[i + 2]
		
		# Generate points along the Bézier curve
		for t_idx in range(1, segments_per_curve + 1):
			var t = float(t_idx) / segments_per_curve
			
			# Quadratic Bézier formula: B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
			var t_inv = 1.0 - t
			var b_point = p0 * (t_inv * t_inv) + p1 * (2.0 * t_inv * t) + p2 * (t * t)
			
			smoothed_path.append(b_point)
	
	# Add the last point
	smoothed_path.append(original_path[-1])
	
	return smoothed_path

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Initialize Random Number Generator (optional but good practice for reproducibility if needed)
	# seed(42) # Uncomment for deterministic paths like Manim example

	# 1. Camera Setup
	var camera := Camera3D.new()
	camera.position = Vector3(0, 0, 15) # Position the camera
	camera.look_at(Vector3.ZERO)       # Make it look towards the origin
	add_child(camera)
	camera.current = true              # Make this the active camera

	# 2. Environment Setup
	var world_env := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = INDIGO
	world_env.environment = env
	add_child(world_env)

	# 3. Lighting Setup
	var light := DirectionalLight3D.new()
	light.position = Vector3(5, 5, 5) # Position the light source
	light.look_at(Vector3.ZERO)      # Point the light towards the origin
	add_child(light)

	# 4. Title Setup (using CanvasLayer for 2D overlay)
	var canvas_layer := CanvasLayer.new()
	add_child(canvas_layer)

	var title_label := Label.new()
	title_label.text = "Path Tracing Animation"
	# Note: Font and exact size might need adjustment after importing a font resource.
	# Using theme defaults for now. Let's set a reasonable font size.
	# title_label.add_theme_font_size_override("font_size", 36) # Requires Godot 4.1+
	# For Godot 4.0 compatibility or if themes are preferred:
	var label_settings = LabelSettings.new()
	label_settings.font_size = 72 # Doubled font size
	title_label.label_settings = label_settings

	# Center the label horizontally and place it near the top
	title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	# Anchors define the control's bounding box relative to its parent.
	# Set anchors for full width, margins for padding.
	title_label.anchor_left = 0.0
	title_label.anchor_right = 1.0
	title_label.anchor_top = 0.0
	title_label.anchor_bottom = 0.0 # Anchor only to top

	# Adjust top margin dynamically based on viewport height
	var viewport_height = get_viewport().size.y
	title_label.offset_top = viewport_height * 0.10 # 10% from the top edge
	# Adjust bottom offset based on new font size to ensure it has space
	title_label.offset_bottom = title_label.offset_top + label_settings.font_size * 1.2 # Approximate height

	canvas_layer.add_child(title_label)

	# 5. Particle Instantiation and Physics State Initialization
	var start_pos = Vector3(0, -1, 0) # Fixed start position

	for config in PARTICLE_CONFIGS:
		# --- Create Particle Mesh (Same as before) ---
		var particle_mesh_instance := MeshInstance3D.new()
		var sphere_mesh := SphereMesh.new()
		sphere_mesh.radius = PARTICLE_RADIUS
		sphere_mesh.height = PARTICLE_RADIUS * 2
		particle_mesh_instance.mesh = sphere_mesh

		# Create Particle Material
		var particle_material := StandardMaterial3D.new()
		particle_material.albedo_color = config["object_color"]
		particle_mesh_instance.material_override = particle_material

		# Generate predefined path
		var path = _generate_particle_path(start_pos)
		particle_paths.append(path)

		# Set initial position to first path point
		particle_mesh_instance.position = path[0]
		add_child(particle_mesh_instance)

		# Start with zero velocity
		particle_velocities.append(Vector3.ZERO)

		# Assign charge based on color
		var charge = 1.0 if config["object_color"] == PURE_RED else -1.0
		particle_charges.append(charge)

		# Initialize empty history
		particle_histories.append([])
		# Add initial state to history
		particle_histories[-1].append([0.0, particle_mesh_instance.position])

		# Store mesh reference (needed for position access and trail)
		particle_meshes.append(particle_mesh_instance)

		# --- Create Trail Rendering Components ---
		var trail_immediate_mesh := ImmediateMesh.new()
		var trail_mesh_node := MeshInstance3D.new()
		trail_mesh_node.mesh = trail_immediate_mesh
		add_child(trail_mesh_node)

		var trail_material := StandardMaterial3D.new()
		trail_material.albedo_color = config["trail_color"]
		trail_material.shading_mode = StandardMaterial3D.SHADING_MODE_UNSHADED
		trail_mesh_node.material_override = trail_material

		trail_mesh_instances.append(trail_mesh_node)
		trail_meshes.append(trail_immediate_mesh)
		trail_materials.append(trail_material)
		trail_points.append(PackedVector3Array())

	# Ensure paths are generated before animation starts
	print("Generated ", particle_paths.size(), " particle paths")


# Helper function to find historical position via interpolation
func _get_historical_position(history: Array, target_time: float) -> Vector3:
	if history.is_empty():
		push_error("History is empty, cannot get historical position.")
		return Vector3.ZERO # Should not happen if initialized correctly
	if target_time <= history[0][0]: # Requesting time before first record
		return history[0][1]
	if target_time >= history[-1][0]: # Requesting time after last record
		return history[-1][1]

	# Binary search or linear scan to find points bracketing target_time
	# Linear scan is simpler for potentially short histories
	for i in range(history.size() - 1):
		var time1: float = history[i][0]
		var pos1: Vector3 = history[i][1]
		var time2: float = history[i+1][0]
		var pos2: Vector3 = history[i+1][1]

		if target_time >= time1 and target_time <= time2:
			if time1 == time2: # Avoid division by zero if timestamps are identical
				return pos1
			# Interpolate
			var t = (target_time - time1) / (time2 - time1)
			return pos1.lerp(pos2, t)

	# Should be unreachable if checks above are correct, but return last known as fallback
	push_warning("Could not find bracketing time in history for interpolation.")
	return history[-1][1]

# Soft boundary force calculation method with more nuanced constraint
func _calculate_boundary_force(particle_pos: Vector3) -> Vector3:
	var force = Vector3.ZERO
	
	# X-axis boundary constraints
	if particle_pos.x < BOUNDS_X_MIN:
		var distance_outside = BOUNDS_X_MIN - particle_pos.x
		force.x = BOUNDARY_SOFTNESS * pow(distance_outside + 1, 3)  # Cubic growth for smoother transition
	elif particle_pos.x > BOUNDS_X_MAX:
		var distance_outside = particle_pos.x - BOUNDS_X_MAX
		force.x = -BOUNDARY_SOFTNESS * pow(distance_outside + 1, 3)
	
	# Y-axis boundary constraints
	if particle_pos.y < BOUNDS_Y_MIN:
		var distance_outside = BOUNDS_Y_MIN - particle_pos.y
		force.y = BOUNDARY_SOFTNESS * pow(distance_outside + 1, 3)
	elif particle_pos.y > BOUNDS_Y_MAX:
		var distance_outside = particle_pos.y - BOUNDS_Y_MAX
		force.y = -BOUNDARY_SOFTNESS * pow(distance_outside + 1, 3)
	
	return force * BOUNDARY_FORCE_MULTIPLIER


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	# Safety check to ensure we have paths and meshes
	if particle_paths.is_empty() or particle_meshes.is_empty():
		return
	
	# Animate particles along their predefined paths
	for i in range(min(particle_meshes.size(), particle_paths.size())):
		var path = particle_paths[i]
		
		# Skip if path is empty
		if path.is_empty():
			continue
		
		var particle_mesh = particle_meshes[i]
		var trail_points = trail_points[i]
		var trail_immediate_mesh = trail_meshes[i]
		var trail_material = trail_materials[i]
		
		# Interpolate position along the path
		var path_progress = min((current_time / 30.0), 1.0) * (path.size() - 1)
		var current_index = min(int(path_progress), path.size() - 2)
		var next_index = current_index + 1
		var t = path_progress - current_index
		
		# Interpolate between path points
		var current_pos = path[current_index].lerp(path[next_index], t)
		particle_mesh.position = current_pos
		
		# Update trail
		if trail_points.is_empty() or not trail_points[-1].is_equal_approx(current_pos):
			trail_points.append(current_pos)
		
		# Redraw trail
		trail_immediate_mesh.clear_surfaces()
		if trail_points.size() > 1:
			trail_immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP, trail_material)
			for point in trail_points:
				trail_immediate_mesh.surface_add_vertex(point)
			trail_immediate_mesh.surface_end()
	
	current_time += delta
