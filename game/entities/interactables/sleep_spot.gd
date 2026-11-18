extends Area2D
## Circe's front door. Going in for the night shows a night's thought; then Circe steps into the
## doorway, the island fades to a starry night with the new day's card (SceneManager), and she
## steps back out onto the doorstep in the morning. The day advances so the moly grows.

const StoryText := preload("res://game/data/story_text.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
## How far Circe walks up into the doorway before the night falls, in pixels.
const STEP_IN := 16.0
## When she steps back out: as the dawn starts (see SceneManager.night_transition).
const BACK_OUT_AFTER := 2.5

## True from the end of the night's thought until Circe is back on the doorstep: the door ignores
## another press meanwhile, so two nights can never overlap.
var _night_in_progress := false

func prompt_text() -> String:
	return "Go inside and sleep"

## No floating label: the prompt says what the door is for.
func world_label() -> Label:
	return null

func interact() -> void:
	if _night_in_progress:
		return
	var day := GameState.current_day
	var thought: Array = StoryText.SLEEP_THOUGHTS[(day - 1) % StoryText.SLEEP_THOUGHTS.size()]
	var box = DialogueBox.open(self, "sleep_day_%d" % day, thought)
	if box and not box.dialogue_ended.is_connected(_on_dialogue_ended):
		box.dialogue_ended.connect(_on_dialogue_ended)

func _on_dialogue_ended(dialogue_id: String) -> void:
	if not dialogue_id.begins_with("sleep_day_"):
		return
	_night_in_progress = true
	GameState.advance_day()
	SceneManager.night_transition(GameState.current_day)
	AudioController.play_sfx("ui_confirm")
	_go_inside()

func _go_inside() -> void:
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if player == null:
		_night_in_progress = false
		return
	player.set_controls_enabled(false)
	var doorstep := Vector2(global_position.x, global_position.y)
	var inside := doorstep + Vector2(0, -STEP_IN)
	var walk_in := create_tween()
	walk_in.tween_property(player, "global_position", inside, 0.4)
	walk_in.parallel().tween_property(player, "modulate:a", 0.0, 0.4)
	await get_tree().create_timer(BACK_OUT_AFTER).timeout
	if not is_instance_valid(player):
		_night_in_progress = false
		return
	player.global_position = doorstep
	var walk_out := create_tween()
	walk_out.tween_property(player, "modulate:a", 1.0, 0.45)
	await walk_out.finished
	_night_in_progress = false
	if is_instance_valid(player):
		player.set_controls_enabled(true)
	print("[Sleep] morning, day %d" % GameState.current_day)   # the playthrough waits for this
