extends Area2D
## Circe's bed. Shows a night's thought, then advances the day so the moly grows.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const StoryText := preload("res://game/data/story_text.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const SLEEP_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/sleep_spot.png"

@onready var sprite: Sprite2D = $Sprite
@onready var day_label: Label = $DayLabel

func _ready() -> void:
	sprite.texture = TextureLoaderUtil.load_texture(SLEEP_TEXTURE_PATH)
	day_label.text = "Rest (Day %d)" % GameState.current_day

func interact() -> void:
	var day := GameState.current_day
	var thought: Array = StoryText.SLEEP_THOUGHTS[(day - 1) % StoryText.SLEEP_THOUGHTS.size()]
	var box = DialogueBox.open(self, "sleep_day_%d" % day, thought)
	if box and not box.dialogue_ended.is_connected(_on_dialogue_ended):
		box.dialogue_ended.connect(_on_dialogue_ended)

func _on_dialogue_ended(dialogue_id: String) -> void:
	if not dialogue_id.begins_with("sleep_day_"):
		return
	GameState.advance_day()
	SceneManager.night_transition(GameState.current_day)
	AudioController.play_sfx("ui_confirm")
	day_label.text = "Rest (Day %d)" % GameState.current_day
