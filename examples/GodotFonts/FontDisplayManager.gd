extends Node3D

# Configuration
const FONT_DIR_PATH: String = "res://"
const DISPLAY_TEXT: String = "The quick brown fox jumps over the lazy dog."
const FONT_SIZE: int = 24
# Decreased pixel size for potentially better resolution
const PIXEL_SIZE: float = 0.005
# Adjusted start Y and spacing slightly due to smaller pixel size
const START_Y: float = 1.5
const VERTICAL_SPACING: float = 0.35

func _ready() -> void:
	print("FontDisplayManager: Starting font loading...")
	_load_and_display_fonts()

func _load_and_display_fonts() -> void:
	# Ensure the path is absolute and print it for debugging
	var absolute_path: String = ProjectSettings.globalize_path(FONT_DIR_PATH)
	print("FontDisplayManager: Attempting to open absolute path: ", absolute_path)

	var dir = DirAccess.open(absolute_path)
	if not dir:
		# Use the absolute path in the error message too
		printerr("FontDisplayManager: Failed to open directory: ", absolute_path)
		return

	var files: PackedStringArray = dir.get_files()
	var label_count: int = 0

	print("FontDisplayManager: Found files: ", files)

	for file_name in files:
		if file_name.ends_with(".tres"):
			var resource_path: String = FONT_DIR_PATH.path_join(file_name)
			print("FontDisplayManager: Attempting to load: ", resource_path)

			var resource = load(resource_path)

			if resource and resource is Font:
				print("FontDisplayManager: Successfully loaded font: ", file_name)
				var font: Font = resource as Font

				var label: Label3D = Label3D.new()

				# Assign font and size directly
				label.font = font
				label.font_size = FONT_SIZE

				# Remove the custom theme creation/assignment

				# Configure the label text, alignment, etc.
				label.text = "%s (%s)" % [DISPLAY_TEXT, file_name]
				label.pixel_size = PIXEL_SIZE
				label.billboard = BaseMaterial3D.BILLBOARD_ENABLED # Make it face the camera
				label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER # Center the text

				# Removed the theme override call that was causing errors

				# Position the label vertically (centered horizontally at x=0)
				label.position.y = START_Y - (label_count * VERTICAL_SPACING)
				label.position.x = 0.0 # Set X to 0 for horizontal centering

				# Add to the scene
				add_child(label)
				label_count += 1
			elif resource:
				printerr("FontDisplayManager: Resource is not a Font: ", resource_path)
			else:
				printerr("FontDisplayManager: Failed to load resource: ", resource_path)

	if label_count == 0:
		print("FontDisplayManager: No .tres font files found or loaded in ", FONT_DIR_PATH)
	else:
		print("FontDisplayManager: Finished. Loaded %d fonts." % label_count)

	# DirAccess should close automatically when 'dir' goes out of scope,
	# but explicit closing is also fine if preferred:
	# dir.close()
