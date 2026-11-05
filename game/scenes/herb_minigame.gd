extends CanvasLayer
## Herb identification minigame: name the herb shown. Three correct answers win.
## Keyboard and controller: left/right move between the answers, A / E / Enter confirm.

signal minigame_completed()

const TextureLoaderUtil = preload("res://game/util/texture_loader.gd")
const UiStyle := preload("res://game/ui/ui_style.gd")
const MOLY_ICON := "res://assets/image_pipeline/generated/raw/sprites/ui/icon_moly.png"
const RIGHT_COLOR := Color(0.62, 0.9, 0.52)
const WRONG_COLOR := Color(1.0, 0.58, 0.48)
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
var _progress_row: HBoxContainer
var _herb_card: PanelContainer
var _wrong_count: int = 0
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
	# The island dims behind the lesson.
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0.04, 0.03, 0.02, 0.6)
	add_child(dim)

	_panel = PanelContainer.new()
	_panel.add_theme_stylebox_override("panel", UiStyle.panel(34, 26, 3))
	var screen := get_viewport().get_visible_rect().size
	var panel_size := Vector2(660, 700)
	_panel.size = panel_size
	_panel.position = (screen - panel_size) / 2.0
	_panel.pivot_offset = panel_size / 2.0
	add_child(_panel)

	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 14)
	_panel.add_child(vbox)

	var title = Label.new()
	title.text = "Hermes' herb lesson"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 32)
	title.add_theme_color_override("font_color", UiStyle.GOLD_TEXT)
	vbox.add_child(title)

	# The herb sits on a cream card, like a page from a herbal.
	var herb_container = CenterContainer.new()
	vbox.add_child(herb_container)
	_herb_card = PanelContainer.new()
	var card := StyleBoxFlat.new()
	card.bg_color = Color(0.93, 0.87, 0.72)
	card.border_color = Color(0.6, 0.45, 0.25)
	card.set_border_width_all(2)
	card.set_corner_radius_all(8)
	card.set_content_margin_all(14)
	_herb_card.add_theme_stylebox_override("panel", card)
	herb_container.add_child(_herb_card)

	_herb_display = TextureRect.new()
	_herb_display.custom_minimum_size = Vector2(240, 240)
	_herb_display.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_herb_display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_herb_display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_herb_card.add_child(_herb_display)

	_hint_label = Label.new()
	_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_hint_label.custom_minimum_size = Vector2(580, 56)
	_hint_label.add_theme_font_size_override("font_size", 20)
	_hint_label.add_theme_color_override("font_color", UiStyle.TEXT)
	vbox.add_child(_hint_label)

	var question = Label.new()
	question.text = "Which herb is this?"
	question.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	question.add_theme_font_size_override("font_size", 20)
	question.add_theme_color_override("font_color", UiStyle.GOLD_TEXT)
	vbox.add_child(question)

	_button_container = HBoxContainer.new()
	_button_container.alignment = BoxContainer.ALIGNMENT_CENTER
	_button_container.add_theme_constant_override("separation", 14)
	vbox.add_child(_button_container)

	var keys = Label.new()
	keys.text = "Left / right to choose, E or Enter to answer"
	keys.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	keys.add_theme_font_size_override("font_size", 15)
	keys.add_theme_color_override("font_color", Color(UiStyle.TEXT, 0.6))
	vbox.add_child(keys)

	_result_label = Label.new()
	_result_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_result_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_result_label.custom_minimum_size = Vector2(580, 30)
	_result_label.add_theme_font_size_override("font_size", 20)
	vbox.add_child(_result_label)

	# Three moly sprigs light up, one per right answer.
	_progress_row = HBoxContainer.new()
	_progress_row.alignment = BoxContainer.ALIGNMENT_CENTER
	_progress_row.add_theme_constant_override("separation", 10)
	vbox.add_child(_progress_row)
	var icon := TextureLoaderUtil.load_texture(MOLY_ICON)
	for i in REQUIRED_CORRECT:
		var sprig := TextureRect.new()
		sprig.texture = icon
		sprig.custom_minimum_size = Vector2(40, 40)
		sprig.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		sprig.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		sprig.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		sprig.modulate = Color(0.25, 0.22, 0.2, 0.8)
		_progress_row.add_child(sprig)

	# The lesson opens with a small pop.
	_panel.scale = Vector2(0.92, 0.92)
	_panel.modulate.a = 0.0
	var pop := create_tween().set_parallel()
	pop.tween_property(_panel, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	pop.tween_property(_panel, "modulate:a", 1.0, 0.2)

func _style_answer(button: Button) -> void:
	button.custom_minimum_size = Vector2(170, 58)
	button.add_theme_font_size_override("font_size", 21)
	button.add_theme_color_override("font_color", UiStyle.TEXT)
	button.add_theme_color_override("font_focus_color", UiStyle.GOLD_TEXT)
	button.add_theme_color_override("font_hover_color", UiStyle.GOLD_TEXT)
	button.add_theme_color_override("font_disabled_color", Color(UiStyle.TEXT, 0.45))
	var normal := UiStyle.panel(12, 8, 1)
	normal.bg_color = Color(0.2, 0.14, 0.09, 0.95)
	normal.border_color = Color(UiStyle.BORDER, 0.5)
	var focus := UiStyle.panel(12, 8, 3)
	focus.bg_color = Color(0.3, 0.21, 0.11, 1.0)
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", focus)
	button.add_theme_stylebox_override("focus", focus)
	button.add_theme_stylebox_override("pressed", focus)
	button.add_theme_stylebox_override("disabled", normal)

func _light_sprigs() -> void:
	for i in _progress_row.get_child_count():
		var sprig: TextureRect = _progress_row.get_child(i)
		var lit := i < _correct_count
		var target := Color(1, 1, 1, 1) if lit else Color(0.25, 0.22, 0.2, 0.8)
		if lit and sprig.modulate != target:
			sprig.pivot_offset = sprig.size / 2.0
			sprig.scale = Vector2(1.5, 1.5)
			create_tween().tween_property(sprig, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK)
		sprig.modulate = target

## A quick wobble of the herb card when the answer is wrong.
func _shake_card() -> void:
	var base := _herb_card.position
	var tween := create_tween()
	for offset in [10.0, -8.0, 6.0, -3.0, 0.0]:
		tween.tween_property(_herb_card, "position:x", base.x + offset, 0.05)

func _show_round() -> void:
	for button in _buttons:
		button.queue_free()
	_buttons.clear()
	_result_label.text = ""
	_light_sprigs()

	var herbs: Array[String] = HERBS.duplicate()
	_current_herb = herbs[_rng.randi_range(0, herbs.size() - 1)]
	_herb_display.texture = TextureLoaderUtil.load_texture(HERB_TEXTURES[_current_herb])
	_hint_label.text = HERB_HINTS[_current_herb]

	herbs.shuffle()
	for herb in herbs:
		var button = Button.new()
		button.text = herb
		_style_answer(button)
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
			_result_label.add_theme_color_override("font_color", RIGHT_COLOR)
			_light_sprigs()
			_disable_buttons()
			await get_tree().create_timer(1.0).timeout
			_set_player_movement(true)
			print("[Minigame] complete")
			minigame_completed.emit()
			AudioController.play_music("world")
			queue_free()
		else:
			var quips: Array = StoryText.MINIGAME_CORRECT_QUIPS
			_result_label.text = quips[(_correct_count - 1) % quips.size()]
			_result_label.add_theme_color_override("font_color", RIGHT_COLOR)
			_light_sprigs()
			_disable_buttons()
			await get_tree().create_timer(1.0).timeout
			_show_round()
	else:
		var quips: Array = StoryText.MINIGAME_WRONG_QUIPS
		_result_label.text = quips[_wrong_count % quips.size()] % _current_herb
		_wrong_count += 1
		_result_label.add_theme_color_override("font_color", WRONG_COLOR)
		_shake_card()
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
		player.set_controls_enabled(enabled)
