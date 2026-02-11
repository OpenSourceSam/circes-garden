extends CanvasLayer

signal minigame_completed()

var _correct_count: int = 0
var _required: int = 3

var _panel: PanelContainer
var _herb_display: ColorRect
var _result_label: Label
var _progress_label: Label
var _button_container: HBoxContainer
var _buttons: Array[Button] = []

func _ready() -> void:
	layer = 20
	_build_ui()
	AudioController.play_music("minigame")
	_show_round()

func _build_ui() -> void:
	# Main panel centered on screen
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.position = Vector2(-250, -200)
	_panel.size = Vector2(500, 400)
	add_child(_panel)

	# VBox for vertical layout
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 12)
	_panel.add_child(vbox)

	# Title
	var title = Label.new()
	title.text = "Identify the Herb"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 20)
	vbox.add_child(title)

	# Spacer
	var spacer1 = Control.new()
	spacer1.custom_minimum_size = Vector2(0, 10)
	vbox.add_child(spacer1)

	# Herb color display (centered container)
	var herb_container = CenterContainer.new()
	vbox.add_child(herb_container)

	_herb_display = ColorRect.new()
	_herb_display.custom_minimum_size = Vector2(120, 120)
	_herb_display.color = Color(0.9, 0.9, 0.3)  # Moly's yellow-green
	herb_container.add_child(_herb_display)

	# Question text
	var question = Label.new()
	question.text = "Which herb is this?"
	question.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(question)

	# Spacer
	var spacer2 = Control.new()
	spacer2.custom_minimum_size = Vector2(0, 10)
	vbox.add_child(spacer2)

	# Button container
	_button_container = HBoxContainer.new()
	_button_container.alignment = BoxContainer.ALIGNMENT_CENTER
	_button_container.add_theme_constant_override("separation", 10)
	vbox.add_child(_button_container)

	# Result label
	_result_label = Label.new()
	_result_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_result_label.add_theme_color_override("font_color", Color.WHITE)
	vbox.add_child(_result_label)

	# Progress label
	_progress_label = Label.new()
	_progress_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_progress_label.add_theme_font_size_override("font_size", 14)
	vbox.add_child(_progress_label)

func _show_round() -> void:
	# Clear previous buttons
	for button in _buttons:
		button.queue_free()
	_buttons.clear()

	# Clear result text
	_result_label.text = ""

	# Update progress
	_progress_label.text = "Progress: %d/%d" % [_correct_count, _required]

	# Create shuffled herb choices
	var herbs: Array[String] = ["Moly", "Nightshade", "Hemlock"]
	herbs.shuffle()

	# Create buttons
	for herb in herbs:
		var button = Button.new()
		button.text = herb
		button.custom_minimum_size = Vector2(130, 50)
		button.pressed.connect(_on_herb_selected.bind(herb))
		_button_container.add_child(button)
		_buttons.append(button)

func _on_herb_selected(herb: String) -> void:
	if herb == "Moly":
		_correct_count += 1
		AudioController.play_sfx("correct")
		if _correct_count >= _required:
			_result_label.text = "Well done!"
			_result_label.add_theme_color_override("font_color", Color.GREEN)
			_disable_buttons()
			await get_tree().create_timer(1.0).timeout
			minigame_completed.emit()
			AudioController.play_music("world")  # Restore world music
			queue_free()
		else:
			_result_label.text = "Correct! (%d/%d)" % [_correct_count, _required]
			_result_label.add_theme_color_override("font_color", Color.GREEN)
			_disable_buttons()
			await get_tree().create_timer(1.0).timeout
			_show_round()
	else:
		_result_label.text = "Wrong! Try again."
		_result_label.add_theme_color_override("font_color", Color.RED)
		AudioController.play_sfx("wrong")
		_disable_buttons()
		await get_tree().create_timer(1.0).timeout
		_show_round()

func _disable_buttons() -> void:
	for button in _buttons:
		button.disabled = true
