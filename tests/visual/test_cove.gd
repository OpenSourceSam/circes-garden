extends Node
## Visual test of Scylla's strait: lands Circe at the cove pier, walks her to the point, plays
## the cure scene and saves a screenshot at each of Scylla's moves, then exits. It renders, so
## it opens a window:
##     Godot --path . res://tests/visual/test_cove.tscn
## Screenshots: tests/visual/screenshots/cove_*.png (gitignored).

const WORLD := "res://game/scenes/world.tscn"
const LANDING := Vector2(272, 2800)
const POINT := Vector2(272, 2508)
## [line of scylla_cure_attempt to show, then [seconds to wait, screenshot name], ...]
const STEPS := [
	[0, [1.0, "cove_roar"]],
	[2, [1.8, "cove_descend"]],
	[6, [0.35, "cove_vial"], [0.5, "cove_vial_caught"]],
	[7, [1.2, "cove_calm"]],
	[9, [0.32, "cove_strike_rear"], [0.24, "cove_strike_hit"], [0.6, "cove_strike_after"]],
	[12, [2.5, "cove_away"]],
]

var _shots := 0

func _ready() -> void:
	call_deferred("_run")

func _run() -> void:
	var root := get_tree().root
	get_parent().remove_child(self)
	root.add_child(self)
	GameState.new_game()
	for flag in ["prologue_complete", "quest_3_complete", "quest_4_active", "can_sail_to_scylla"]:
		GameState.set_flag(flag, true)
	GameState.add_item("calming_draught", 1)
	SceneManager.change_scene(WORLD)
	await SceneManager.transition_finished

	var player := get_tree().get_first_node_in_group("player") as Node2D
	var camera := get_viewport().get_camera_2d()
	player.global_position = LANDING
	camera.reset_smoothing()
	await _wait(1.2)
	await _shot("cove_landing")
	player.global_position = POINT
	camera.reset_smoothing()
	await _wait(1.5)
	await _shot("cove_sea")

	var scylla := get_tree().current_scene.get_node("Scylla")
	scylla.interact()
	var box = get_tree().get_first_node_in_group("dialogue_box")
	for step in STEPS:
		_show_line(box, step[0])
		for shot in step.slice(1):
			await _wait(shot[0])
			await _shot(shot[1])
	print("[CoveTest] %d screenshots in tests/visual/screenshots/" % _shots)
	get_tree().quit()

## Moves the dialogue on to line `n` (each press first finishes the typing, then advances).
func _show_line(box, n: int) -> void:
	while box.is_active() and box._current_line_index < n:
		if box._typing:
			box.advance()
		box.advance()

func _wait(seconds: float) -> Signal:
	return get_tree().create_timer(seconds).timeout

func _shot(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/visual/screenshots"))
	var image := get_viewport().get_texture().get_image()
	image.save_png("res://tests/visual/screenshots/%s.png" % shot_name)
	_shots += 1
