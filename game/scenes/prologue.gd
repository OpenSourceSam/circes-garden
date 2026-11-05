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
var _page_label: Label
var _background: ColorRect
var _overlay: ColorRect
var _image_rect: TextureRect
var _transitioning: bool = false
var _drift: Tween

func _ready() -> void:
	_build_ui()
	_show_screen(0)

func _build_ui() -> void:
	var size := get_viewport_rect().size
	_background = ColorRect.new()
	_background.set_anchors_preset(Control.PRESET_FULL_RECT)
	_background.color = Color.BLACK
	add_child(_background)

	_image_rect = TextureRect.new()
	_image_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	# The paintings are 864x1184; cover the portrait viewport, then drift slowly (see _show_screen).
	_image_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_image_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_image_rect.pivot_offset = size / 2.0
	add_child(_image_rect)

	# A light tint in each screen's mood, so the paintings stay visible.
	_overlay = ColorRect.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.color = Color(0, 0, 0, 0.2)
	add_child(_overlay)

	# A dark band rising from the bottom carries the words.
	var veil := TextureRect.new()
	var gradient := Gradient.new()
	gradient.offsets = PackedFloat32Array([0.0, 0.55, 1.0])
	gradient.colors = PackedColorArray([Color(0.05, 0.03, 0.02, 0.0), Color(0.05, 0.03, 0.02, 0.15), Color(0.05, 0.03, 0.02, 0.93)])
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0.5, 0.0)
	texture.fill_to = Vector2(0.5, 1.0)
	texture.width = 2
	texture.height = 128
	veil.texture = texture
	veil.stretch_mode = TextureRect.STRETCH_SCALE
	veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(veil)

	_text_label = Label.new()
	_text_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_text_label.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.add_theme_font_size_override("font_size", 30)
	_text_label.add_theme_constant_override("line_spacing", 6)
	_text_label.add_theme_color_override("font_color", Color(0.98, 0.95, 0.86))
	_text_label.add_theme_color_override("font_outline_color", Color(0.08, 0.05, 0.03, 0.9))
	_text_label.add_theme_constant_override("outline_size", 8)
	_text_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_text_label.offset_left = 110
	_text_label.offset_right = -110
	_text_label.offset_top = -420
	_text_label.offset_bottom = -130
	add_child(_text_label)

	_page_label = Label.new()
	_page_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_page_label.add_theme_font_size_override("font_size", 18)
	_page_label.add_theme_color_override("font_color", Color(0.95, 0.82, 0.52, 0.85))
	_page_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_page_label.offset_left = 40
	_page_label.offset_right = 300
	_page_label.offset_top = -64
	_page_label.offset_bottom = -34
	add_child(_page_label)

	_prompt_label = Label.new()
	_prompt_label.text = "Enter  continue      Esc  skip"
	_prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_prompt_label.add_theme_font_size_override("font_size", 18)
	_prompt_label.add_theme_color_override("font_color", Color(0.95, 0.92, 0.84, 0.8))
	_prompt_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_prompt_label.offset_left = -460
	_prompt_label.offset_right = -40
	_prompt_label.offset_top = -64
	_prompt_label.offset_bottom = -34
	add_child(_prompt_label)
	var pulse := create_tween().set_loops()
	pulse.tween_property(_prompt_label, "modulate:a", 0.55, 1.2).set_trans(Tween.TRANS_SINE)
	pulse.tween_property(_prompt_label, "modulate:a", 1.0, 1.2).set_trans(Tween.TRANS_SINE)

func _show_screen(index: int) -> void:
	if index >= _screens.size():
		_finish_prologue()
		return

	_current_screen = index
	var screen: Dictionary = _screens[index]
	_text_label.text = screen["text"]
	_page_label.text = "%d / %d" % [index + 1, _screens.size()]
	_image_rect.texture = TextureLoaderUtil.load_texture(screen["image"])

	var mood: Color = screen["overlay"]
	var overlay_tween := create_tween()
	overlay_tween.tween_property(_overlay, "color", Color(mood.r, mood.g, mood.b, 0.22), 0.35)

	_image_rect.modulate = Color(1, 1, 1, 0)
	_text_label.modulate = Color(1, 1, 1, 0)
	var fade_in := create_tween()
	fade_in.parallel().tween_property(_image_rect, "modulate", Color(1, 1, 1, 1), 0.6)
	fade_in.parallel().tween_property(_text_label, "modulate", Color(1, 1, 1, 1), 0.9).set_delay(0.15)

	# A slow push-in on every painting, alternating its direction, like a camera breathing.
	if _drift:
		_drift.kill()
	var start_scale := 1.0 if index % 2 == 0 else 1.07
	var end_scale := 1.07 if index % 2 == 0 else 1.0
	_image_rect.scale = Vector2(start_scale, start_scale)
	_drift = create_tween()
	_drift.tween_property(_image_rect, "scale", Vector2(end_scale, end_scale), 12.0).set_trans(Tween.TRANS_SINE)

func _unhandled_input(event: InputEvent) -> void:
	if _transitioning:
		return
	if event.is_action_pressed("ui_cancel"):
		AudioController.play_sfx("ui_confirm")
		_finish_prologue()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		_current_screen += 1
		AudioController.play_sfx("ui_move")
		_show_screen(_current_screen)
		get_viewport().set_input_as_handled()

func _finish_prologue() -> void:
	_transitioning = true
	_prompt_label.hide()
	_page_label.hide()
	_text_label.text = ""

	var tween := create_tween()
	tween.parallel().tween_property(_overlay, "color", Color.BLACK, 0.8)
	tween.parallel().tween_property(_image_rect, "modulate", Color(1, 1, 1, 0), 0.8)
	tween.tween_callback(func():
		SceneManager.change_scene("res://game/scenes/world.tscn")
	)
