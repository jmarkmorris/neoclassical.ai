extends Node

func _ready():
	# Create the opacity scene programmatically
	var opacity_scene = Node2D.new()
	opacity_scene.set_script(load("res://opacity_scene.gd"))
	add_child(opacity_scene)
