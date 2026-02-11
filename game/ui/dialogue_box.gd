extends CanvasLayer

signal dialogue_started(dialogue_id: String)
signal dialogue_ended(dialogue_id: String)

# Node references - built programmatically
var panel: PanelContainer
var speaker_label: Label
var dialogue_label: Label
var continue_prompt: Label

var _current_dialogue: DialogueData = null
var _current_line_index: int = 0
var _is_active: bool = false

func _ready() -> void:
	add_to_group("dialogue_box")
	_build_ui()
	hide_box()

func _build_ui() -> void:
	# Create main panel container
	panel = PanelContainer.new()
	panel.name = "Panel"
	add_child(panel)

	# Configure panel styling
	var style_box = StyleBoxFlat.new()
	style_box.bg_color = Color(0.1, 0.1, 0.1, 0.9)
	style_box.border_color = Color(0.3, 0.3, 0.3, 1.0)
	style_box.border_width_left = 2
	style_box.border_width_right = 2
	style_box.border_width_top = 2
	style_box.border_width_bottom = 2
	style_box.content_margin_left = 20
	style_box.content_margin_right = 20
	style_box.content_margin_top = 15
	style_box.content_margin_bottom = 15
	panel.add_theme_stylebox_override("panel", style_box)

	# Position panel: bottom-center, portrait-friendly
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	var viewport_width := get_viewport().get_visible_rect().size.x
	var box_width := minf(viewport_width - 100.0, 900.0)
	panel.offset_left = (viewport_width - box_width) / 2.0
	panel.offset_right = panel.offset_left + box_width
	panel.offset_bottom = -30
	panel.offset_top = panel.offset_bottom - 200

	# Create VBoxContainer for layout
	var vbox = VBoxContainer.new()
	vbox.name = "VBox"
	panel.add_child(vbox)

	# Speaker label (bold, larger)
	speaker_label = Label.new()
	speaker_label.name = "SpeakerLabel"
	speaker_label.add_theme_font_size_override("font_size", 20)
	speaker_label.add_theme_color_override("font_color", Color(0.9, 0.8, 0.6, 1.0))  # Warm color
	vbox.add_child(speaker_label)

	# Spacer
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 5)
	vbox.add_child(spacer)

	# Dialogue label (main text, word wrap)
	dialogue_label = Label.new()
	dialogue_label.name = "DialogueLabel"
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.add_theme_font_size_override("font_size", 16)
	dialogue_label.add_theme_color_override("font_color", Color(1, 1, 1, 1))
	dialogue_label.custom_minimum_size = Vector2(820, 80)  # Ensure space for text
	vbox.add_child(dialogue_label)

	# Bottom spacer with continue prompt
	var bottom_container = HBoxContainer.new()
	bottom_container.name = "BottomContainer"
	vbox.add_child(bottom_container)

	# Spacer to push prompt to right
	var push_right = Control.new()
	push_right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bottom_container.add_child(push_right)

	# Continue prompt
	continue_prompt = Label.new()
	continue_prompt.name = "ContinuePrompt"
	continue_prompt.text = "[E] Continue"
	continue_prompt.add_theme_font_size_override("font_size", 12)
	continue_prompt.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7, 1.0))
	bottom_container.add_child(continue_prompt)

func _unhandled_input(event: InputEvent) -> void:
	if not _is_active:
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		advance()
		get_viewport().set_input_as_handled()

func start_dialogue(dialogue: DialogueData) -> void:
	# Check flags_required - if any flag not set, don't start
	for flag in dialogue.flags_required:
		if not GameState.get_flag(flag):
			return

	_current_dialogue = dialogue
	_current_line_index = 0
	_is_active = true
	show_box()
	AudioController.play_sfx("ui_open")
	_display_current_line()
	dialogue_started.emit(dialogue.id)

	# Disable player movement
	_set_player_movement(false)

func advance() -> void:
	AudioController.play_sfx("ui_move")
	_current_line_index += 1
	if _current_line_index >= _current_dialogue.lines.size():
		end_dialogue()
	else:
		_display_current_line()

func _display_current_line() -> void:
	var line = _current_dialogue.lines[_current_line_index]
	speaker_label.text = line.get("speaker", "")
	dialogue_label.text = line.get("text", "")

func end_dialogue() -> void:
	# Set flags
	for flag in _current_dialogue.flags_to_set:
		GameState.set_flag(flag, true)

	var dialogue_id = _current_dialogue.id
	_current_dialogue = null
	_is_active = false
	AudioController.play_sfx("ui_close")
	hide_box()
	_set_player_movement(true)
	dialogue_ended.emit(dialogue_id)

func show_box() -> void:
	panel.show()

func hide_box() -> void:
	panel.hide()

func _set_player_movement(enabled: bool) -> void:
	var player = get_tree().get_first_node_in_group("player")
	if player:
		player.set_physics_process(enabled)

func is_active() -> bool:
	return _is_active
