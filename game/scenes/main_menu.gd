extends Control
## Title screen. Start begins a new game with the prologue.

const StoryText := preload("res://game/data/story_text.gd")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")

@onready var title_label: Label = $CenterContainer/VBoxContainer/TitleLabel
@onready var start_button: Button = $CenterContainer/VBoxContainer/StartButton

func _ready() -> void:
	_setup_gradient_background()
	title_label.text = StoryText.MENU["title"]
	_add_subtitle()
	start_button.pressed.connect(_on_start_pressed)
	start_button.grab_focus()
	AudioController.play_music("menu")

func _setup_gradient_background() -> void:
	var bg := $Background
	var tex_rect := TextureRect.new()
	tex_rect.texture = TextureLoaderUtil.vertical_gradient(Color(0.18, 0.15, 0.12), Color(0.08, 0.06, 0.05))
	tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
	tex_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.add_sibling(tex_rect)
	move_child(tex_rect, bg.get_index())
	bg.queue_free()

func _add_subtitle() -> void:
	# Sits directly under the title inside the existing VBoxContainer.
	var subtitle := Label.new()
	subtitle.name = "SubtitleLabel"
	subtitle.text = StoryText.MENU["subtitle"]
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 16)
	subtitle.add_theme_color_override("font_color", Color(0.72, 0.66, 0.58))
	title_label.add_sibling(subtitle)

func _on_start_pressed() -> void:
	AudioController.play_sfx("ui_confirm")
	GameState.new_game()
	SceneManager.change_scene("res://game/scenes/prologue.tscn")
