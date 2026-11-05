extends CanvasLayer
## Herb identification minigame: name the herb shown. Three correct answers win.
## Keyboard and controller: left/right move between the answers, A / E / Enter confirm.

signal minigame_completed()

const TextureLoaderUtil = preload("res://game/util/texture_loader.gd")
const StoryText := preload("res://game/data/story_text.gd")
const HERB_TEXTURES := {
	"Moly": "res://assets/image_pipeline/generated/raw/sprites/ui/herb_moly.png",
	"Nightshade": "res://assets/image_pipeline/generated/raw/sprites/ui/herb_nightshade.png",
	"Hemlock": "res://assets/image_pipeline/generated/raw/sprites/ui/herb_hemlock.png",
}
const HERB_HINTS := StoryText.HERB_HINTS

const REQUIRED_CORRECT := 3
const HERBS: Array[String] = ["Moly", "Nightshade", "Hemlock"]

var _correct_count: int = 0
var _current_herb: String = ""
var _busy: bool = false

var _panel: PanelContainer
var _herb_display: TextureRect
var _hint_label: Label
var _result_label: Label
var _progress_label: Label
var _button_container: HBoxContainer
var _buttons: Array[Button] = []
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	layer = 20
	_rng.randomize()
	_build_ui()
	_set_player_movement(false)
	AudioController.play_music("minigame")
	_show_round()

func _build_ui() -> void:
	_panel = PanelContainer.new()
	_panel.set_anchors_preset(Control.PRESET_CENTER)
	_panel.position = Vector2(-250, -230)
	_panel.size = Vector2(500, 460)
	add_child(_panel)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	_panel.add_child(vbox)

	var title = Label.new()
	title.text = "Identify the Herb"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 22)
	vbox.add_child(title)

	var herb_container = CenterContainer.new()
	vbox.add_child(herb_container)

	_herb_display = TextureRect.new()
	_herb_display.custom_minimum_size = Vector2(192, 192)
	_herb_display.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_herb_display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_herb_display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	herb_container.add_child(_herb_display)

	_hint_label = Label.new()
	_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_hint_label.custom_minimum_size = Vector2(460, 0)
	_hint_label.add_theme_font_size_override("font_size", 14)
	_hint_label.add_theme_color_override("font_color", Color(0.85, 0.82, 0.7))
	vbox.add_child(_hint_label)

	var question = Label.new()
	question.text = "Which herb is this?  (left / right, then A / E)"
	question.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(question)

	_button_container = HBoxContainer.new()
	_button_container.alignment = BoxContainer.ALIGNMENT_CENTER
	_button_container.add_theme_constant_override("separation", 10)
	vbox.add_child(_button_container)

	_result_label = Label.new()
	_result_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_result_label.add_theme_color_override("font_color", Color.WHITE)
	vbox.add_child(_result_label)

	_progress_label = Label.new()
	_progress_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_progress_label.add_theme_font_size_override("font_size", 14)
	vbox.add_child(_progress_label)

func _show_round() -> void:
	for button in _buttons:
		button.queue_free()
	_buttons.clear()
	_result_label.text = ""
	_result_label.add_theme_color_override("font_color", Color.WHITE)
	_progress_label.text = "Progress: %d/%d" % [_correct_count, REQUIRED_CORRECT]

	var herbs: Array[String] = HERBS.duplicate()
	_current_herb = herbs[_rng.randi_range(0, herbs.size() - 1)]
	_herb_display.texture = TextureLoaderUtil.load_texture(HERB_TEXTURES[_current_herb])
	_hint_label.text = HERB_HINTS[_current_herb]

	herbs.shuffle()
	for herb in herbs:
		var button = Button.new()
		button.text = herb
		button.custom_minimum_size = Vector2(130, 50)
		button.focus_mode = Control.FOCUS_ALL
		button.pressed.connect(_on_herb_selected.bind(herb))
		_button_container.add_child(button)
		_buttons.append(button)
	_busy = false
	print("[Minigame] round %d, showing %s" % [_correct_count + 1, _current_herb])
	if _buttons.size() > 1:
		_buttons[1].call_deferred("grab_focus")

func _unhandled_input(event: InputEvent) -> void:
	# Keep E / A from reaching the world while the minigame is open.
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		if _busy:
			return
		var focused := get_viewport().gui_get_focus_owner()
		if focused is Button and _buttons.has(focused):
			(focused as Button).pressed.emit()
		elif _buttons.size() > 1:
			_buttons[1].grab_focus()
	elif event.is_action_pressed("ui_left") or event.is_action_pressed("ui_right"):
		var focused := get_viewport().gui_get_focus_owner()
		if not (focused is Button and _buttons.has(focused)) and _buttons.size() > 1:
			_buttons[1].grab_focus()
			get_viewport().set_input_as_handled()

func _on_herb_selected(herb: String) -> void:
	if _busy:
		return
	_busy = true
	if herb == _current_herb:
		_correct_count += 1
		AudioController.play_sfx("correct")
		if _correct_count >= REQUIRED_CORRECT:
			_result_label.text = StoryText.MINIGAME_TEXT["win"]
			_result_label.add_theme_color_override("font_color", Color.GREEN)
			_disable_buttons()
			await get_tree().create_timer(1.0).timeout
			_set_player_movement(true)
			print("[Minigame] complete")
			minigame_completed.emit()
			AudioController.play_music("world")
			queue_free()
		else:
			_result_label.text = StoryText.MINIGAME_TEXT["correct"] % [_correct_count, REQUIRED_CORRECT]
			_result_label.add_theme_color_override("font_color", Color.GREEN)
			_disable_buttons()
			await get_tree().create_timer(1.0).timeout
			_show_round()
	else:
		_result_label.text = StoryText.MINIGAME_TEXT["wrong"] % _current_herb
		_result_label.add_theme_color_override("font_color", Color(1.0, 0.45, 0.4))
		AudioController.play_sfx("wrong")
		_disable_buttons()
		await get_tree().create_timer(1.2).timeout
		_show_round()

func _disable_buttons() -> void:
	for button in _buttons:
		button.disabled = true

func _set_player_movement(enabled: bool) -> void:
	var player = get_tree().get_first_node_in_group("player")
	if player:
		player.set_physics_process(enabled)
		player.set_process_unhandled_input(enabled)
