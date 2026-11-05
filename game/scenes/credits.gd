extends Control
## End credits over the garden painting. E or Enter returns to the title screen.

const StoryText := preload("res://game/data/story_text.gd")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const UiStyle := preload("res://game/ui/ui_style.gd")
const PAINTING_PATH := "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_07.png"

@onready var title_label: Label = $CenterContainer/VBoxContainer/TitleLabel
@onready var body_label: Label = $CenterContainer/VBoxContainer/BodyLabel
@onready var prompt_label: Label = $CenterContainer/VBoxContainer/PromptLabel

func _ready() -> void:
	_setup_background()
	title_label.text = StoryText.CREDITS["title"]
	body_label.text = StoryText.CREDITS["body"]
	prompt_label.text = StoryText.CREDITS["prompt"]
	title_label.add_theme_font_override("font", UiStyle.TITLE_FONT)
	for label in [title_label, body_label, prompt_label]:
		label.add_theme_color_override("font_outline_color", Color(0.06, 0.04, 0.03, 0.9))
		label.add_theme_constant_override("outline_size", 8)
	AudioController.play_music("epilogue")
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 1.6)

## The garden painting, darkened: the story ends where the title screen began.
func _setup_background() -> void:
	var bg := $Background
	var painting := TextureRect.new()
	painting.texture = TextureLoaderUtil.load_texture(PAINTING_PATH)
	painting.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	painting.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	painting.set_anchors_preset(Control.PRESET_FULL_RECT)
	painting.modulate = Color(0.42, 0.38, 0.36)
	bg.add_sibling(painting)
	move_child(painting, bg.get_index())
	bg.queue_free()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		AudioController.play_sfx("ui_confirm")
		SceneManager.change_scene("res://game/scenes/main_menu.tscn")
		get_viewport().set_input_as_handled()
