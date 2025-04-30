extends Node

func _ready():
	print("main.gd: _ready() called") # DEBUG
	# Create the opacity scene programmatically
	var opacity_scene = load("res://opacity_scene.gd").new()
	add_child(opacity_scene)
