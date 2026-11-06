extends Node
## QA capture: loads the world, hides the interface and the drifting pollen, and saves the island
## at the game's own scale (camera zoom 2, 1080 x 1240) in overlapping shots from top to bottom.
## Run: Godot --path <project> res://tools/capture/capture_island.tscn -- <out_dir>

const SHOT_CENTRES := [Vector2(270, 310), Vector2(270, 760), Vector2(270, 1194)]

func _ready() -> void:
	var out_dir := "user://qa"
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		out_dir = args[0]
	DirAccess.make_dir_recursive_absolute(out_dir)
	var world: Node = load("res://game/scenes/world.tscn").instantiate()
	add_child(world)
	for i in 10:
		await get_tree().process_frame
	for child in world.get_children():
		if child is CanvasLayer:
			child.visible = false
		if child is CPUParticles2D or child is GPUParticles2D:
			child.visible = false
	var camera: Camera2D = world.find_child("Camera2D", true, false)
	camera.reparent(world)
	camera.position_smoothing_enabled = false
	camera.make_current()
	for i in SHOT_CENTRES.size():
		camera.global_position = SHOT_CENTRES[i]
		camera.reset_smoothing()
		for f in 6:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := "%s/island_%d.png" % [out_dir, i + 1]
		img.save_png(path)
		print("[Capture] saved ", path, " ", img.get_size())
	get_tree().quit()
