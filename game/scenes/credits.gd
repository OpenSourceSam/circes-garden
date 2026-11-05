extends Control
## End credits. A / E returns to the title screen.

const StoryText := preload("res://game/data/story_text.gd")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")

@onready var title_label: Label = $CenterContainer/VBoxContainer/TitleLabel
@onready var body_label: Label = $CenterContainer/VBoxContainer/BodyLabel
@onready var prompt_label: Label = $CenterContainer/VBoxContainer/PromptLabel

func _ready() -> void:
	_setup_background_gradient()
	title_label.text = StoryText.CREDITS["title"]
	body_label.text = StoryText.CREDITS["body"]
	prompt_label.text = StoryText.CREDITS["prompt"]
	AudioController.play_music("epilogue")

func _setup_background_gradient() -> void:
	var bg := $Background
	var tex_rect := TextureRect.new()
	tex_rect.texture = TextureLoaderUtil.vertical_gradient(Color(0.08, 0.1, 0.15), Color(0.02, 0.03, 0.05))
	tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
	tex_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.add_sibling(tex_rect)
	move_child(tex_rect, bg.get_index())
	bg.queue_free()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		AudioController.play_sfx("ui_confirm")
		SceneManager.change_scene("res://game/scenes/main_menu.tscn")
		get_viewport().set_input_as_handled()
