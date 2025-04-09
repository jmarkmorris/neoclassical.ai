extends Node3D

# Enum for tip styles for clarity
enum TipStyle {
	TRIANGLE,
	TRIANGLE_FILLED,
	SQUARE,
	SQUARE_FILLED,
	CIRCLE,
	CIRCLE_FILLED,
	STEALTH
}

# Constants
const WHITE: Color = Color.WHITE
const YELLOW: Color = Color.YELLOW

const TITLE_FONT_SIZE: int = 36
const SUBTITLE_FONT_SIZE: int = 20
const LABEL_FONT_SIZE: int = 24

const AXIS_LENGTH: float = 1.5
const AXIS_THICKNESS: float = 0.06 # Used for CSG thickness. ImmediateMesh lines remain thin.
const TICK_LENGTH: float = 0.1
const TIP_SIZE: float = 0.15 # Base size, will be adjusted per tip

const GRID_COLS: int = 4
const GRID_H_SPACING: float = 3.25
const GRID_V_SPACING: float = 2.5

# Preload a basic material for lines/unshaded shapes
var unshaded_white_material: StandardMaterial3D

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	# Create the material once
	unshaded_white_material = StandardMaterial3D.new()
	unshaded_white_material.albedo_color = WHITE
	unshaded_white_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED

	_setup_text_elements()
	_setup_axes_grid()


func _setup_text_elements() -> void:
	# Title
	var title_label := Label3D.new()
	title_label.text = "Arrow Tips Showcase"
	title_label.font_size = TITLE_FONT_SIZE
	title_label.modulate = WHITE
	title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER # Helps centering
	title_label.position = Vector3(0, 4.0, 0) # Adjust Y as needed
	add_child(title_label)


func _setup_axes_grid() -> void:
	var tip_styles: Array[TipStyle] = [
		TipStyle.TRIANGLE,
		TipStyle.TRIANGLE_FILLED,
		TipStyle.SQUARE,
		TipStyle.SQUARE_FILLED,
		TipStyle.CIRCLE,
		TipStyle.CIRCLE_FILLED,
		TipStyle.STEALTH
	]

	# Use names directly from the enum for consistency if possible, or map if needed
	var tip_names: Dictionary = {
		TipStyle.TRIANGLE: "ArrowTriangleTip",
		TipStyle.TRIANGLE_FILLED: "ArrowTriangleFilledTip",
		TipStyle.SQUARE: "ArrowSquareTip",
		TipStyle.SQUARE_FILLED: "ArrowSquareFilledTip",
		TipStyle.CIRCLE: "ArrowCircleTip",
		TipStyle.CIRCLE_FILLED: "ArrowCircleFilledTip",
		TipStyle.STEALTH: "StealthTip"
	}

	var start_x: float = -((GRID_COLS - 1) * GRID_H_SPACING) / 2.0
	# Adjust start_y based on image (lower than initial guess)
	var start_y: float = 1.5

	for i in range(tip_styles.size()):
		var tip_style: TipStyle = tip_styles[i]
		var col: int = i % GRID_COLS
		var row: int = i / GRID_COLS

		var pos_x: float = start_x + col * GRID_H_SPACING
		var pos_y: float = start_y - row * GRID_V_SPACING

		_create_axes_example(tip_style, tip_names[tip_style], Vector3(pos_x, pos_y, 0))


func _create_axes_example(tip_style: TipStyle, tip_name: String, position: Vector3) -> void:
	# Container for this example
	var container := Node3D.new()
	container.name = tip_name # Set node name for easier debugging
	container.position = position
	add_child(container)

	# Label for the tip style
	var label := Label3D.new()
	label.text = tip_name
	label.font_size = LABEL_FONT_SIZE
	label.modulate = WHITE
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	# Adjust label position based on image
	label.position = Vector3(0, AXIS_LENGTH / 2.0 + 0.8, 0)
	container.add_child(label)

	# Draw axes, ticks, and tips
	_draw_axes_lines(container)
	_draw_ticks(container)
	_draw_arrow_tips(container, tip_style)

# --- Drawing Helper Functions ---

func _draw_axes_lines(parent: Node3D) -> void:
	# Horizontal Axis using CSGBox3D
	var x_axis := CSGBox3D.new()
	x_axis.size = Vector3(AXIS_LENGTH, AXIS_THICKNESS, AXIS_THICKNESS * 0.5) # Make slightly flatter
	x_axis.material = unshaded_white_material
	parent.add_child(x_axis)

	# Vertical Axis using CSGBox3D
	var y_axis := CSGBox3D.new()
	y_axis.size = Vector3(AXIS_THICKNESS, AXIS_LENGTH, AXIS_THICKNESS * 0.5) # Make slightly flatter
	y_axis.material = unshaded_white_material
	parent.add_child(y_axis)


func _draw_ticks(parent: Node3D) -> void:
	var tick_size_x := Vector3(AXIS_THICKNESS, TICK_LENGTH, AXIS_THICKNESS * 0.5)
	var tick_size_y := Vector3(TICK_LENGTH, AXIS_THICKNESS, AXIS_THICKNESS * 0.5)

	# Tick on negative X axis
	var x_tick := CSGBox3D.new()
	x_tick.size = tick_size_x
	x_tick.position = Vector3(-AXIS_LENGTH / 2.0, 0, 0)
	x_tick.material = unshaded_white_material
	parent.add_child(x_tick)

	# Tick on negative Y axis
	var y_tick := CSGBox3D.new()
	y_tick.size = tick_size_y
	y_tick.position = Vector3(0, -AXIS_LENGTH / 2.0, 0)
	y_tick.material = unshaded_white_material
	parent.add_child(y_tick)


func _draw_arrow_tips(parent: Node3D, tip_style: TipStyle) -> void:
	var x_tip_pos := Vector3(AXIS_LENGTH / 2.0, 0, 0)
	var y_tip_pos := Vector3(0, AXIS_LENGTH / 2.0, 0)

	# Draw tip on positive X axis
	_draw_single_tip(parent, tip_style, unshaded_white_material, x_tip_pos, Vector3.RIGHT)
	# Draw tip on positive Y axis
	_draw_single_tip(parent, tip_style, unshaded_white_material, y_tip_pos, Vector3.UP)


func _draw_single_tip(parent: Node3D, tip_style: TipStyle, material: StandardMaterial3D, position: Vector3, direction: Vector3) -> void:
	# Create a container Node3D for the tip elements to handle rotation easily
	var tip_container := Node3D.new()
	tip_container.position = position
	tip_container.rotate_z(Vector3.RIGHT.angle_to(direction))
	parent.add_child(tip_container)

	match tip_style:
		TipStyle.TRIANGLE:
			_draw_triangle_tip(tip_container, material, false)
		TipStyle.TRIANGLE_FILLED:
			_draw_triangle_tip(tip_container, material, true)
		TipStyle.SQUARE:
			_draw_square_tip(tip_container, material, false)
		TipStyle.SQUARE_FILLED:
			_draw_square_tip(tip_container, material, true)
		TipStyle.CIRCLE:
			_draw_circle_tip(tip_container, material, false)
		TipStyle.CIRCLE_FILLED:
			_draw_circle_tip(tip_container, material, true)
		TipStyle.STEALTH:
			_draw_stealth_tip(tip_container, material) # Stealth is always filled


# --- Specific Tip Drawing Functions ---

# Helper to create an ImmediateMesh line loop
func _create_line_loop(parent: Node3D, material: StandardMaterial3D, points: PackedVector3Array) -> void:
	if points.size() < 2: return

	var im_mesh := ImmediateMesh.new()
	var mesh_inst := MeshInstance3D.new()
	mesh_inst.mesh = im_mesh
	parent.add_child(mesh_inst) # Add MeshInstance to the container

	im_mesh.surface_begin(Mesh.PRIMITIVE_LINE_STRIP, material) # Use LINE_STRIP for connected lines
	for point in points:
		im_mesh.surface_add_vertex(point)
	# Add the first point again to close the loop
	im_mesh.surface_add_vertex(points[0])
	im_mesh.surface_end()


func _draw_triangle_tip(parent: Node3D, material: StandardMaterial3D, filled: bool) -> void:
	var size := TIP_SIZE
	# Define vertices relative to origin (0,0,0) within the parent container
	var p1 := Vector3(0, 0, 0) # Tip point at origin
	var p2 := Vector3(-size, size / 2.0, 0)
	var p3 := Vector3(-size, -size / 2.0, 0)

	if filled:
		var polygon := CSGPolygon3D.new()
		polygon.polygon = PackedVector2Array([Vector2(p1.x, p1.y), Vector2(p2.x, p2.y), Vector2(p3.x, p3.y)]) # Use Vector2 for CSGPolygon
		polygon.material = material
		polygon.mode = CSGPolygon3D.MODE_DEPTH
		polygon.depth = AXIS_THICKNESS * 0.5 # Minimal depth
		# No position/rotation needed as parent container handles it
		parent.add_child(polygon)
	else: # Outline
		var points := PackedVector3Array([p1, p2, p3])
		_create_line_loop(parent, material, points)


func _draw_square_tip(parent: Node3D, material: StandardMaterial3D, filled: bool) -> void:
	var size := TIP_SIZE * 0.8 # Adjust size for square
	# Define vertices relative to origin (0,0,0)
	var p1 := Vector3(0, 0, 0) # Tip point at origin
	var p2 := Vector3(-size, size, 0)
	var p3 := Vector3(-size * 2.0, 0, 0)
	var p4 := Vector3(-size, -size, 0)

	if filled:
		var polygon := CSGPolygon3D.new()
		polygon.polygon = PackedVector2Array([Vector2(p1.x, p1.y), Vector2(p2.x, p2.y), Vector2(p3.x, p3.y), Vector2(p4.x, p4.y)])
		polygon.material = material
		polygon.mode = CSGPolygon3D.MODE_DEPTH
		polygon.depth = AXIS_THICKNESS * 0.5
		parent.add_child(polygon)
	else: # Outline
		var points := PackedVector3Array([p1, p2, p3, p4])
		_create_line_loop(parent, material, points)


func _draw_circle_tip(parent: Node3D, material: StandardMaterial3D, filled: bool) -> void:
	var radius := TIP_SIZE * 0.6 # Adjust size for circle
	var segments := 16 # Number of segments for outline circle

	if filled:
		var circle := CSGCylinder3D.new()
		circle.radius = radius
		circle.height = AXIS_THICKNESS * 0.5
		circle.sides = segments # Make it smooth
		circle.material = material
		# Position center of circle relative to the axis end point (which is parent's origin)
		circle.position = Vector3(-radius, 0, 0) # Move center back along local X
		circle.rotation = Vector3(PI / 2.0, 0, 0) # Orient flat along XY plane
		parent.add_child(circle)
	else: # Outline
		var points := PackedVector3Array()
		var center := Vector3(-radius, 0, 0) # Center of the circle relative to parent origin
		for i in range(segments + 1): # +1 to close loop smoothly with LINE_STRIP
			var angle = TAU * float(i) / segments
			var x = center.x + cos(angle) * radius
			var y = center.y + sin(angle) * radius
			points.append(Vector3(x, y, 0))

		# Use a separate helper for non-closed line strip if needed, but line loop works
		_create_line_loop(parent, material, points)


func _draw_stealth_tip(parent: Node3D, material: StandardMaterial3D) -> void:
	var length := TIP_SIZE * 1.5
	var width_ratio := 0.5 # Width relative to length

	# Define vertices relative to origin (0,0,0)
	var p1 := Vector3(0, 0, 0) # Tip point at origin
	var p2 := Vector3(-length, length * width_ratio * 0.5, 0)
	var p3 := Vector3(-length * 0.7, 0, 0) # Indent point
	var p4 := Vector3(-length, -length * width_ratio * 0.5, 0)

	# Stealth tip is always filled
	var polygon := CSGPolygon3D.new()
	polygon.polygon = PackedVector2Array([Vector2(p1.x, p1.y), Vector2(p2.x, p2.y), Vector2(p3.x, p3.y), Vector2(p4.x, p4.y)])
	polygon.material = material
	polygon.mode = CSGPolygon3D.MODE_DEPTH
	polygon.depth = AXIS_THICKNESS * 0.5
	parent.add_child(polygon)
