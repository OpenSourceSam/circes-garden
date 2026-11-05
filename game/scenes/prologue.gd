extends Control
## The prologue: seven narrated screens over the February 2026 paintings, then the world.

const TextureLoaderUtil = preload("res://game/util/texture_loader.gd")
const StoryText := preload("res://game/data/story_text.gd")

var _screens: Array = [
	{
		"text": StoryText.PROLOGUE[0],
		"overlay": Color(0.08, 0.05, 0.08, 0.55),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_01.png",
	},
	{
		"text": StoryText.PROLOGUE[1],
		"overlay": Color(0.06, 0.08, 0.07, 0.55),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_02.png",
	},
	{
		"text": StoryText.PROLOGUE[2],
		"overlay": Color(0.1, 0.06, 0.06, 0.6),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_03.png",
	},
	{
		"text": StoryText.PROLOGUE[3],
		"overlay": Color(0.12, 0.05, 0.05, 0.62),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_04.png",
	},
	{
		"text": StoryText.PROLOGUE[4],
		"overlay": Color(0.11, 0.04, 0.05, 0.65),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_05.png",
	},
	{
		"text": StoryText.PROLOGUE[5],
		"overlay": Color(0.06, 0.06, 0.09, 0.58),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_06.png",
	},
	{
		"text": StoryText.PROLOGUE[6],
		"overlay": Color(0.06, 0.08, 0.05, 0.58),
		"image": "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_07.png",
	},
]

var _current_screen: int = 0
var _text_label: Label
var _prompt_label: Label
var _background: ColorRect
var _overlay: ColorRect
var _image_rect: TextureRect
var _transitioning: bool = false

func _ready() -> void:
	_build_ui()
	_show_screen(0)

func _build_ui() -> void:
	_background = ColorRect.new()
	_background.set_anchors_preset(Control.PRESET_FULL_RECT)
	_background.color = Color.BLACK
	add_child(_background)

	_image_rect = TextureRect.new()
	_image_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	# The paintings are 864x1184; keep their aspect ratio inside the portrait viewport.
	_image_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_image_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_image_rect.modulate = Color(1, 1, 1, 1)
	add_child(_image_rect)

	_overlay = ColorRect.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.color = Color(0, 0, 0, 0.55)
	add_child(_overlay)

	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var vbox := VBoxContainer.new()
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	vbox.add_theme_constant_override("separation", 40)
	center.add_child(vbox)

	_text_label = Label.new()
	_text_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.custom_minimum_size = Vector2(800, 0)
	_text_label.add_theme_font_size_override("font_size", 24)
	_text_label.add_theme_color_override("font_color", Color(0.95, 0.92, 0.82))
	vbox.add_child(_text_label)

	_prompt_label = Label.new()
	_prompt_label.text = "[A / E] Continue"
	_prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt_label.add_theme_font_size_override("font_size", 14)
	_prompt_label.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))
	_prompt_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_prompt_label.offset_top = -60
	_prompt_label.offset_bottom = -30
	add_child(_prompt_label)

func _show_screen(index: int) -> void:
	if index >= _screens.size():
		_finish_prologue()
		return

	_current_screen = index
	var screen: Dictionary = _screens[index]
	_text_label.text = screen["text"]
	_image_rect.texture = TextureLoaderUtil.load_texture(screen["image"])

	var overlay_tween := create_tween()
	overlay_tween.tween_property(_overlay, "color", screen["overlay"], 0.35)

	_image_rect.modulate = Color(1, 1, 1, 0)
	_text_label.modulate = Color(1, 1, 1, 0)
	var fade_in := create_tween()
	fade_in.parallel().tween_property(_image_rect, "modulate", Color(1, 1, 1, 1), 0.5)
	fade_in.parallel().tween_property(_text_label, "modulate", Color(1, 1, 1, 1), 0.65)

func _unhandled_input(event: InputEvent) -> void:
	if _transitioning:
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		_current_screen += 1
		AudioController.play_sfx("ui_move")
		_show_screen(_current_screen)
		get_viewport().set_input_as_handled()

func _finish_prologue() -> void:
	_transitioning = true
	_prompt_label.hide()
	_text_label.text = ""

	var tween := create_tween()
	tween.parallel().tween_property(_overlay, "color", Color.BLACK, 0.8)
	tween.parallel().tween_property(_image_rect, "modulate", Color(1, 1, 1, 0), 0.8)
	tween.tween_callback(func():
		SceneManager.change_scene("res://game/scenes/world.tscn")
	)
