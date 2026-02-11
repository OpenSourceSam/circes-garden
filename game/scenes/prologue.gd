extends Control
## Prologue: Narrated backstory before gameplay begins
## Shows sequential text screens about Circe and Scylla's history

var _screens: Array = [
	{
		"text": "Long ago, on the island of Aiaia,\nthere lived a goddess named Circe.",
		"color": Color(0.15, 0.12, 0.18),
	},
	{
		"text": "Daughter of Helios, she mastered\nthe art of pharmaka —\nthe magic of herbs and potions.",
		"color": Color(0.12, 0.15, 0.18),
	},
	{
		"text": "She loved Glaucus, the sea-god.\nBut Glaucus loved Scylla.",
		"color": Color(0.18, 0.12, 0.12),
	},
	{
		"text": "In jealousy, Circe poured poison\ninto Scylla's bathing pool.",
		"color": Color(0.2, 0.1, 0.1),
	},
	{
		"text": "Scylla transformed.\nSix heads. Twelve legs.\nA ring of snarling dogs at her waist.",
		"color": Color(0.15, 0.08, 0.08),
	},
	{
		"text": "Now Circe lives in exile,\nhaunted by what she has done.",
		"color": Color(0.1, 0.1, 0.15),
	},
	{
		"text": "Perhaps pharmaka can undo\nwhat pharmaka has done...",
		"color": Color(0.12, 0.14, 0.1),
	},
]

var _current_screen: int = 0
var _text_label: Label
var _prompt_label: Label
var _background: ColorRect
var _transitioning: bool = false

func _ready() -> void:
	_build_ui()
	_show_screen(0)

func _build_ui() -> void:
	# Dark background
	_background = ColorRect.new()
	_background.set_anchors_preset(Control.PRESET_FULL_RECT)
	_background.color = Color(0.1, 0.1, 0.1, 1)
	add_child(_background)

	# Center container for text
	var center := CenterContainer.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(center)

	var vbox := VBoxContainer.new()
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	vbox.add_theme_constant_override("separation", 40)
	center.add_child(vbox)

	# Main text
	_text_label = Label.new()
	_text_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.custom_minimum_size = Vector2(800, 0)
	_text_label.add_theme_font_size_override("font_size", 24)
	_text_label.add_theme_color_override("font_color", Color(0.9, 0.85, 0.75))
	vbox.add_child(_text_label)

	# Continue prompt at bottom
	_prompt_label = Label.new()
	_prompt_label.text = "[E] Continue"
	_prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt_label.add_theme_font_size_override("font_size", 14)
	_prompt_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
	_prompt_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_prompt_label.offset_top = -60
	_prompt_label.offset_bottom = -30
	add_child(_prompt_label)

func _show_screen(index: int) -> void:
	if index >= _screens.size():
		_finish_prologue()
		return

	_current_screen = index
	var screen = _screens[index]
	_text_label.text = screen["text"]

	# Fade background color
	var tween := create_tween()
	tween.tween_property(_background, "color", screen["color"], 0.5)

	# Fade text in
	_text_label.modulate = Color(1, 1, 1, 0)
	var text_tween := create_tween()
	text_tween.tween_property(_text_label, "modulate", Color(1, 1, 1, 1), 0.8)

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

	# Fade to black, then transition to world
	var tween := create_tween()
	tween.tween_property(_background, "color", Color.BLACK, 1.0)
	tween.tween_callback(func():
		SceneManager.change_scene("res://game/scenes/world.tscn")
	)
