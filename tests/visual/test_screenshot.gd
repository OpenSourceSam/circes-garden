extends Node
## Visual test: Capture screenshots of game scenes then exit
## Launch: Godot --path . res://tests/visual/test_screenshot.tscn
## This node reparents itself to /root so it survives scene changes.

var _screenshots_taken: int = 0
var _scenes_to_test: Array[Dictionary] = []
var _current_scene_index: int = -1
var _post_render_frames: int = 0
var _capturing: bool = false

func _ready() -> void:
	print("\n[VisualTest] Starting headed screenshot test...")

	# Move ourselves to root so we survive scene changes
	call_deferred("_reparent_to_root")

	_scenes_to_test = [
		{"path": "res://game/scenes/main_menu.tscn", "name": "main_menu"},
		{"path": "res://game/scenes/prologue.tscn", "name": "prologue"},
		{"path": "res://game/scenes/world.tscn", "name": "world"},
	]

	SceneManager.transition_finished.connect(_on_transition_finished)
	# Defer first scene load so reparent happens first
	call_deferred("_load_next_scene")

func _reparent_to_root() -> void:
	var tree_root = get_tree().root
	var parent = get_parent()
	parent.remove_child(self)
	tree_root.add_child(self)

func _load_next_scene() -> void:
	_current_scene_index += 1
	if _current_scene_index >= _scenes_to_test.size():
		print("[VisualTest] All %d screenshots captured!" % _screenshots_taken)
		print("[VisualTest] Saved to: tests/visual/screenshots/")
		get_tree().quit()
		return

	var scene_info = _scenes_to_test[_current_scene_index]
	print("[VisualTest] Loading: %s" % scene_info["path"])
	# Initialize game state for world scene (matches normal Start Game flow)
	if scene_info["name"] == "world":
		GameState.new_game()
	SceneManager.change_scene(scene_info["path"])

func _on_transition_finished() -> void:
	_post_render_frames = 0
	_capturing = true

func _process(_delta: float) -> void:
	if not _capturing:
		return

	_post_render_frames += 1
	if _post_render_frames >= 30:
		_capturing = false
		var scene_info = _scenes_to_test[_current_scene_index]
		_take_screenshot(scene_info["name"])
		_load_next_scene()

func _take_screenshot(scene_name: String) -> void:
	var dir = DirAccess.open("res://")
	if not dir.dir_exists("tests/visual/screenshots"):
		dir.make_dir_recursive("tests/visual/screenshots")

	var image: Image = get_viewport().get_texture().get_image()
	var path = "res://tests/visual/screenshots/%s.png" % scene_name
	var err = image.save_png(path)
	if err == OK:
		print("[VisualTest] Screenshot saved: %s (%dx%d)" % [path, image.get_width(), image.get_height()])
		_screenshots_taken += 1
	else:
		print("[VisualTest] FAILED to save: %s (error %d)" % [path, err])
