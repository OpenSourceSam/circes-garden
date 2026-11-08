extends CanvasLayer
## Hermes' flash cards. He shows herbs one at a time, pictures only, and Circe picks them back in the
## same order from five cards, two of them harmless look-alikes (wild carrot, bilberry). Three rounds:
## 3 cards, then 4, then 5. A wrong herb or running out of time is a failure: Hermes drinks the brew,
## the colour drains, the screen flashes twice and shakes, and he falls over. After two failures in one
## round he shows one card fewer, so nobody is stuck here.
## Keyboard and controller: left/right move between the herbs, A / E / Enter pick. Mouse and touch: click.

signal minigame_completed()

const TextureLoaderUtil = preload("res://game/util/texture_loader.gd")
const UiStyle := preload("res://game/ui/ui_style.gd")
const StoryText := preload("res://game/data/story_text.gd")
const MOLY_ICON := "res://assets/image_pipeline/generated/raw/sprites/ui/icon_moly.png"
const CARD_FLOWER := "res://assets/image_pipeline/generated/raw/sprites/ui/card_back_flower.png"
const HERB_PATH := "res://assets/image_pipeline/generated/raw/sprites/ui/herb_%s.png"
const RIGHT_COLOR := Color(0.62, 0.9, 0.52)
const WRONG_COLOR := Color(1.0, 0.58, 0.48)
const CARD_CREAM := Color(0.93, 0.87, 0.72)
const CARD_EDGE := Color(0.6, 0.45, 0.25)
const INK := Color(0.16, 0.11, 0.08)

const HERBS: Array[String] = ["moly", "nightshade", "hemlock", "wild_carrot", "bilberry"]
const REAL_HERBS: Array[String] = ["moly", "nightshade", "hemlock"]
const NAMES := {
	"moly": "Moly", "nightshade": "Nightshade", "hemlock": "Hemlock",
	"wild_carrot": "Wild carrot", "bilberry": "Bilberry",
}
const ROUNDS: Array[int] = [3, 4, 5]
const SHOW_SECONDS := 1.5
const ANSWER_SECONDS_PER_CARD := 3.0
const ROW_WIDTH := 660.0

## The colour drain and the negative flash, over everything on screen.
const FX_SHADER := """
shader_type canvas_item;
uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform float gray = 0.0;
uniform float negative = 0.0;
void fragment() {
	vec3 c = texture(screen_tex, SCREEN_UV).rgb;
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	vec3 g = mix(c, vec3(l), gray);
	COLOR = vec4(mix(g, vec3(1.0) - g, negative), 1.0);
}
"""

## Set by hermes.gd, so he can drink the brew and fall over.
var hermes: Node2D

var _round: int = 0
var _round_fails: int = 0
var _length_cut: int = 0
var _extra_show: float = 0.0
var _wrong_lines: int = 0
var _slow_lines: int = 0
var _sequence: Array[String] = []
var _picked: int = 0
var _state: String = "start"     # start, watch, repeat, busy, failed
var _time_left: float = 0.0
var _time_total: float = 0.0
var _last_tick: int = 99
var _run_id: int = 0
var _hermes_pose := {}
var _rng := RandomNumberGenerator.new()
var _textures := {}

var _dim: ColorRect
var _panel: PanelContainer
var _say_label: Label
var _phase_label: Label
var _timer_bar: ProgressBar
var _count_label: Label
var _cards_row: HBoxContainer
var _cards: Array[PanelContainer] = []
var _choices_row: HBoxContainer
var _choices: Array[Button] = []
var _result_label: Label
var _again_button: Button
var _progress_row: HBoxContainer
var _fx_rect: ColorRect
var _fx: ShaderMaterial
var _speech: PanelContainer
var _speech_label: Label

func _ready() -> void:
	layer = 20
	_rng.randomize()
	for herb in HERBS:
		_textures[herb] = TextureLoaderUtil.load_texture(HERB_PATH % herb)
	_textures["back"] = TextureLoaderUtil.load_texture(CARD_FLOWER)
	_build_ui()
	_set_player_movement(false)
	AudioController.play_music("minigame")
	_say(StoryText.FLASH_TEXT["intro"])
	_build_cards(ROUNDS[0], "back")
	await get_tree().create_timer(2.6).timeout
	_start_round()

# ---------------------------------------------------------------- building the panel

func _build_ui() -> void:
	# The island dims behind the lesson.
	_dim = ColorRect.new()
	_dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_dim.color = Color(0.04, 0.03, 0.02, 0.6)
	_dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_dim)

	_panel = PanelContainer.new()
	_panel.add_theme_stylebox_override("panel", UiStyle.panel(34, 24, 3))
	var screen := get_viewport().get_visible_rect().size
	var panel_size := Vector2(740, 840)
	_panel.size = panel_size
	_panel.position = (screen - panel_size) / 2.0
	_panel.pivot_offset = panel_size / 2.0
	add_child(_panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 12)
	_panel.add_child(vbox)

	var title := _label("Hermes' Flash Cards", 30, UiStyle.GOLD_TEXT)
	title.add_theme_font_override("font", UiStyle.TITLE_FONT)
	vbox.add_child(title)

	_say_label = _label("", 24, Color(0.93, 0.85, 0.66))
	_say_label.add_theme_font_override("font", UiStyle.ITALIC_FONT)
	_say_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_say_label.custom_minimum_size = Vector2(660, 64)
	vbox.add_child(_say_label)

	# Status: what to do now, the answer timer, and which card is showing.
	var status := HBoxContainer.new()
	status.add_theme_constant_override("separation", 14)
	status.custom_minimum_size = Vector2(0, 30)
	vbox.add_child(status)
	_phase_label = _label("", 24, UiStyle.GOLD_TEXT)
	_phase_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_phase_label.add_theme_font_override("font", UiStyle.TITLE_FONT)
	status.add_child(_phase_label)
	_timer_bar = ProgressBar.new()
	_timer_bar.show_percentage = false
	_timer_bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_timer_bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_timer_bar.custom_minimum_size = Vector2(0, 14)
	_timer_bar.max_value = 1.0
	_timer_bar.step = 0.0
	var bar_bg := StyleBoxFlat.new()
	bar_bg.bg_color = Color(0.29, 0.21, 0.14)
	bar_bg.set_corner_radius_all(7)
	var bar_fill := StyleBoxFlat.new()
	bar_fill.bg_color = UiStyle.GOLD_TEXT
	bar_fill.set_corner_radius_all(7)
	_timer_bar.add_theme_stylebox_override("background", bar_bg)
	_timer_bar.add_theme_stylebox_override("fill", bar_fill)
	status.add_child(_timer_bar)
	_count_label = _label("", 22, Color(UiStyle.TEXT, 0.8))
	_count_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_count_label.custom_minimum_size = Vector2(90, 0)
	_count_label.size_flags_horizontal = Control.SIZE_SHRINK_END
	status.add_child(_count_label)

	# The cards Hermes shows; in Circe's turn the same row holds her answers.
	_cards_row = HBoxContainer.new()
	_cards_row.alignment = BoxContainer.ALIGNMENT_CENTER
	_cards_row.add_theme_constant_override("separation", 12)
	_cards_row.custom_minimum_size = Vector2(0, 190)
	vbox.add_child(_cards_row)

	# Five herbs to pick from, in a new order every round.
	_choices_row = HBoxContainer.new()
	_choices_row.alignment = BoxContainer.ALIGNMENT_CENTER
	_choices_row.add_theme_constant_override("separation", 10)
	vbox.add_child(_choices_row)
	for herb in HERBS:
		var button := _make_choice(herb)
		_choices_row.add_child(button)
		_choices.append(button)

	var hint := _label(StoryText.FLASH_TEXT["lookalikes"], 20, Color(UiStyle.TEXT, 0.75))
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hint.custom_minimum_size = Vector2(660, 0)
	vbox.add_child(hint)

	_result_label = _label("", 24, RIGHT_COLOR)
	_result_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_result_label.custom_minimum_size = Vector2(660, 32)
	vbox.add_child(_result_label)

	var bottom := HBoxContainer.new()
	bottom.alignment = BoxContainer.ALIGNMENT_CENTER
	bottom.add_theme_constant_override("separation", 24)
	vbox.add_child(bottom)
	_again_button = Button.new()
	_again_button.text = "Try again"
	_style_again(_again_button)
	_again_button.pressed.connect(_on_again)
	_again_button.hide()
	bottom.add_child(_again_button)

	# Three moly sprigs light up, one per round won.
	_progress_row = HBoxContainer.new()
	_progress_row.alignment = BoxContainer.ALIGNMENT_CENTER
	_progress_row.add_theme_constant_override("separation", 10)
	bottom.add_child(_progress_row)
	var icon := TextureLoaderUtil.load_texture(MOLY_ICON)
	for i in ROUNDS.size():
		var sprig := TextureRect.new()
		sprig.texture = icon
		sprig.custom_minimum_size = Vector2(40, 40)
		sprig.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		sprig.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		sprig.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		sprig.modulate = Color(0.25, 0.22, 0.2, 0.8)
		_progress_row.add_child(sprig)

	var keys := _label("Left / right to choose, E or Enter to pick, or click", 20, Color(UiStyle.TEXT, 0.7))
	vbox.add_child(keys)

	_set_choices_shown(false)

	# Hermes' line after a failure, at the bottom of the screen while the panel is away.
	_speech = PanelContainer.new()
	_speech.add_theme_stylebox_override("panel", UiStyle.panel(26, 16, 3))
	_speech.size = Vector2(680, 0)
	_speech.position = Vector2((screen.x - 680) / 2.0, screen.y - 190)
	_speech.modulate.a = 0.0
	_speech.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_speech)
	var speech_box := VBoxContainer.new()
	_speech.add_child(speech_box)
	var who := _label("HERMES", 22, UiStyle.GOLD_TEXT)
	who.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	who.add_theme_font_override("font", UiStyle.TITLE_FONT)
	speech_box.add_child(who)
	_speech_label = _label("", 26, UiStyle.TEXT)
	_speech_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_speech_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_speech_label.custom_minimum_size = Vector2(628, 0)
	speech_box.add_child(_speech_label)

	# The screen effect sits above everything, switched on only for a failure.
	var fx_layer := CanvasLayer.new()
	fx_layer.layer = 90
	add_child(fx_layer)
	_fx_rect = ColorRect.new()
	_fx_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fx_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var shader := Shader.new()
	shader.code = FX_SHADER
	_fx = ShaderMaterial.new()
	_fx.shader = shader
	_fx_rect.material = _fx
	_fx_rect.hide()
	fx_layer.add_child(_fx_rect)

	# The lesson opens with a small pop.
	_panel.scale = Vector2(0.92, 0.92)
	_panel.modulate.a = 0.0
	var pop := create_tween().set_parallel()
	pop.tween_property(_panel, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	pop.tween_property(_panel, "modulate:a", 1.0, 0.2)

func _label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label

func _card_style(kind: String) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.set_corner_radius_all(10)
	box.set_border_width_all(3)
	box.set_content_margin_all(8)
	match kind:
		"back":
			box.bg_color = Color(0.42, 0.29, 0.17)
			box.border_color = Color(0.56, 0.4, 0.25)
		"face", "ok":
			box.bg_color = CARD_CREAM
			box.border_color = CARD_EDGE
		"bad":
			box.bg_color = Color(0.95, 0.79, 0.75)
			box.border_color = WRONG_COLOR
		"now":
			box.bg_color = Color(0.23, 0.17, 0.11)
			box.border_color = UiStyle.GOLD_TEXT
		_:
			box.bg_color = Color(0.23, 0.17, 0.11)
			box.border_color = Color(0.42, 0.3, 0.18)
	return box

func _build_cards(n: int, kind: String) -> void:
	for card in _cards:
		card.queue_free()
	_cards.clear()
	var w := minf(150.0, floorf((ROW_WIDTH - 12.0 * (n - 1)) / n))
	for i in n:
		var card := PanelContainer.new()
		card.custom_minimum_size = Vector2(w, roundf(w * 1.25))
		card.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var pic := TextureRect.new()
		pic.name = "Pic"
		pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		pic.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		card.add_child(pic)
		var num := _label("", 30, Color(0.55, 0.42, 0.27))
		num.name = "Num"
		num.add_theme_font_override("font", UiStyle.TITLE_FONT)
		num.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		card.add_child(num)
		_cards_row.add_child(card)
		_cards.append(card)
		_set_card(i, kind)

## kind: back (face down), face (showing herb), empty / now (Circe's answer slots), ok / bad (her answers).
func _set_card(i: int, kind: String, herb: String = "") -> void:
	var card := _cards[i]
	card.add_theme_stylebox_override("panel", _card_style(kind))
	var pic: TextureRect = card.get_node("Pic")
	var num: Label = card.get_node("Num")
	num.text = ""
	pic.texture = null
	match kind:
		"back":
			pic.texture = _textures["back"]
			pic.custom_minimum_size = Vector2(44, 44)
			pic.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
			pic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		"face", "ok", "bad":
			pic.texture = _textures[herb]
			pic.custom_minimum_size = Vector2.ZERO
			pic.size_flags_horizontal = Control.SIZE_FILL
			pic.size_flags_vertical = Control.SIZE_FILL
		"now":
			num.text = "?"
			num.add_theme_color_override("font_color", UiStyle.GOLD_TEXT)
		_:
			num.text = str(i + 1)
			num.add_theme_color_override("font_color", Color(0.55, 0.42, 0.27))

## A face-down card turns over (or back) by squashing to nothing and opening again.
func _flip(i: int, kind: String, herb: String = "") -> void:
	var card := _cards[i]
	card.pivot_offset = card.size / 2.0
	var close := create_tween()
	close.tween_property(card, "scale:x", 0.04, 0.12).set_ease(Tween.EASE_IN)
	await close.finished
	_set_card(i, kind, herb)
	var open := create_tween()
	open.tween_property(card, "scale:x", 1.0, 0.12).set_ease(Tween.EASE_OUT)
	await open.finished

func _make_choice(herb: String) -> Button:
	var button := Button.new()
	button.custom_minimum_size = Vector2(124, 150)
	button.focus_mode = Control.FOCUS_ALL
	var normal := _card_style("face")
	var focus := _card_style("face")
	focus.border_color = Color(0.85, 0.55, 0.1)
	focus.set_border_width_all(5)
	focus.bg_color = Color(0.98, 0.93, 0.8)
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", focus)
	button.add_theme_stylebox_override("focus", focus)
	button.add_theme_stylebox_override("pressed", focus)
	button.add_theme_stylebox_override("disabled", normal)
	var box := VBoxContainer.new()
	box.set_anchors_preset(Control.PRESET_FULL_RECT)
	box.offset_top = 6
	box.offset_bottom = -6
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	button.add_child(box)
	var pic := TextureRect.new()
	pic.texture = _textures[herb]
	pic.custom_minimum_size = Vector2(96, 96)
	pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	pic.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(pic)
	var name_label := _label(NAMES[herb], 20, INK)
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(name_label)
	button.pressed.connect(_on_choice.bind(herb))
	button.set_meta("herb", herb)
	return button

func _style_again(button: Button) -> void:
	button.custom_minimum_size = Vector2(220, 58)
	button.add_theme_font_size_override("font_size", 25)
	button.add_theme_color_override("font_color", UiStyle.TEXT)
	button.add_theme_color_override("font_focus_color", UiStyle.GOLD_TEXT)
	button.add_theme_color_override("font_hover_color", UiStyle.GOLD_TEXT)
	var normal := UiStyle.panel(12, 8, 1)
	normal.bg_color = Color(0.2, 0.14, 0.09, 0.95)
	var focus := UiStyle.panel(12, 8, 3)
	focus.bg_color = Color(0.3, 0.21, 0.11, 1.0)
	button.add_theme_stylebox_override("normal", normal)
	button.add_theme_stylebox_override("hover", focus)
	button.add_theme_stylebox_override("focus", focus)
	button.add_theme_stylebox_override("pressed", focus)

func _set_choices_shown(shown: bool) -> void:
	_choices_row.modulate.a = 1.0 if shown else 0.0
	for button in _choices:
		button.disabled = not shown
		button.focus_mode = Control.FOCUS_ALL if shown else Control.FOCUS_NONE

func _light_sprigs() -> void:
	for i in _progress_row.get_child_count():
		var sprig: TextureRect = _progress_row.get_child(i)
		var lit := i < _round
		var target := Color(1, 1, 1, 1) if lit else Color(0.25, 0.22, 0.2, 0.8)
		if lit and sprig.modulate != target:
			sprig.pivot_offset = sprig.size / 2.0
			sprig.scale = Vector2(1.5, 1.5)
			create_tween().tween_property(sprig, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK)
		sprig.modulate = target

func _say(text: String) -> void:
	_say_label.text = "Hermes: “%s”" % text

# ---------------------------------------------------------------- the rounds

func _make_sequence(n: int) -> Array[String]:
	for _try in 200:
		var seq: Array[String] = []
		while seq.size() < n:
			var herb: String = HERBS[_rng.randi_range(0, HERBS.size() - 1)]
			if seq.size() > 0 and seq[-1] == herb:
				continue
			seq.append(herb)
		# From the second round on, at least one look-alike is in his cards.
		var has_lookalike := false
		for herb in seq:
			if not REAL_HERBS.has(herb):
				has_lookalike = true
		if _round == 0 or has_lookalike:
			return seq
	var fallback: Array[String] = []
	for i in n:
		fallback.append(HERBS[i % HERBS.size()])
	return fallback

func _start_round() -> void:
	_run_id += 1
	var my := _run_id
	var n := maxi(2, ROUNDS[_round] - _length_cut)
	_sequence = _make_sequence(n)
	_picked = 0
	_state = "watch"
	_again_button.hide()
	_result_label.text = ""
	_set_choices_shown(false)
	_timer_bar.hide()
	_phase_label.text = "Watch"
	_say(StoryText.FLASH_TEXT["watch"])
	_build_cards(n, "back")
	print("[Minigame] round %d, %d cards" % [_round + 1, n])
	await get_tree().create_timer(0.7).timeout
	for i in n:
		if my != _run_id:
			return
		_count_label.text = "%d of %d" % [i + 1, n]
		await _flip(i, "face", _sequence[i])
		await get_tree().create_timer(SHOW_SECONDS + _extra_show).timeout
		if my != _run_id:
			return
		await _flip(i, "back")
		await get_tree().create_timer(0.15).timeout
	if my == _run_id:
		_begin_repeat()

func _begin_repeat() -> void:
	var n := _sequence.size()
	_state = "repeat"
	_phase_label.text = "Your turn"
	_say(StoryText.FLASH_TEXT["repeat"])
	for i in n:
		_set_card(i, "now" if i == 0 else "empty")
	# The five herbs in a new order every round.
	var order := _choices.duplicate()
	order.shuffle()
	for i in order.size():
		_choices_row.move_child(order[i], i)
	_set_choices_shown(true)
	var answer: Array[String] = []
	for herb in _sequence:
		for i in _choices_row.get_child_count():
			if _choices_row.get_child(i).get_meta("herb") == herb:
				answer.append(str(i))
	# The automated playthrough reads this line to pick the right herbs.
	print("[Minigame] answer %s" % ",".join(answer))
	(_choices_row.get_child(0) as Button).grab_focus()
	_time_total = ANSWER_SECONDS_PER_CARD * n
	_time_left = _time_total
	_last_tick = 99
	_timer_bar.value = 1.0
	_timer_bar.show()

func _process(delta: float) -> void:
	if _state != "repeat":
		return
	_time_left -= delta
	_timer_bar.value = maxf(0.0, _time_left / _time_total)
	_count_label.text = "%.1f s" % maxf(0.0, _time_left)
	var fill: StyleBoxFlat = _timer_bar.get_theme_stylebox("fill")
	fill.bg_color = WRONG_COLOR if _time_left < 3.0 else UiStyle.GOLD_TEXT
	# A tick each second for the last three.
	var whole := ceili(_time_left)
	if _time_left < 3.0 and whole < _last_tick:
		_last_tick = whole
		AudioController.play_sfx("urgency")
	if _time_left <= 0.0:
		_fail("slow")

func _on_choice(herb: String) -> void:
	if _state != "repeat":
		return
	if herb != _sequence[_picked]:
		_set_card(_picked, "bad", herb)
		_fail("wrong")
		return
	_set_card(_picked, "ok", herb)
	AudioController.play_sfx("correct")
	_picked_next()

func _picked_next() -> void:
	_picked += 1
	if _picked < _sequence.size():
		_set_card(_picked, "now")
		return
	_picked = 0
	_win_round()

func _win_round() -> void:
	_state = "busy"
	_timer_bar.hide()
	_count_label.text = ""
	_set_choices_shown(false)
	_round += 1
	_round_fails = 0
	_length_cut = 0
	_extra_show = 0.0
	_light_sprigs()
	_result_label.add_theme_color_override("font_color", RIGHT_COLOR)
	if _round >= ROUNDS.size():
		_phase_label.text = "Lesson passed"
		_result_label.text = StoryText.FLASH_TEXT["win"]
		AudioController.play_sfx("harvest")
		await get_tree().create_timer(1.6).timeout
		_set_player_movement(true)
		print("[Minigame] complete")
		minigame_completed.emit()
		AudioController.play_music("world")
		queue_free()
		return
	var quips: Array = StoryText.MINIGAME_CORRECT_QUIPS
	_result_label.text = quips[(_round - 1) % quips.size()]
	await get_tree().create_timer(1.4).timeout
	_start_round()

# ---------------------------------------------------------------- the failure moment

## He drinks it, the colour drains, two negative flashes (under the safe limit of three in any one
## second), he falls over, the screen shakes, the failure sound plays and he mocks you.
func _fail(kind: String) -> void:
	_state = "busy"
	_picked = 0
	_round_fails += 1
	_set_choices_shown(false)
	_timer_bar.hide()
	_count_label.text = ""
	_phase_label.text = "Too slow" if kind == "slow" else "Wrong herb"
	print("[Minigame] failed: %s" % kind)
	AudioController.play_sfx("wrong")
	await get_tree().create_timer(0.35).timeout
	# The panel steps aside so the player sees Hermes.
	var away := create_tween().set_parallel()
	away.tween_property(_panel, "modulate:a", 0.0, 0.2)
	away.tween_property(_dim, "color:a", 0.0, 0.2)
	await away.finished
	_fx_rect.show()
	_fx.set_shader_parameter("negative", 0.0)
	_fx.set_shader_parameter("gray", 1.0)
	await get_tree().create_timer(0.15).timeout
	for i in 2:
		_fx.set_shader_parameter("negative", 1.0)
		await get_tree().create_timer(0.09).timeout
		_fx.set_shader_parameter("negative", 0.0)
		await get_tree().create_timer(0.11).timeout
	_topple_hermes(true)
	SceneManager.shake_camera(0.45, 8.0)
	_shake_node(_speech)
	AudioController.play_sfx("failure")
	if kind == "slow":
		_speech_label.text = StoryText.FLASH_FAIL_SLOW[_slow_lines % StoryText.FLASH_FAIL_SLOW.size()]
		_slow_lines += 1
	else:
		_speech_label.text = StoryText.FLASH_FAIL_WRONG[_wrong_lines % StoryText.FLASH_FAIL_WRONG.size()]
		_wrong_lines += 1
	_speech.modulate.a = 1.0
	_say(_speech_label.text)
	# The colour comes back slowly while he lies there.
	var recover := create_tween()
	recover.tween_method(func(v: float): _fx.set_shader_parameter("gray", v), 1.0, 0.0, 0.9)
	await get_tree().create_timer(2.4).timeout
	_fx_rect.hide()
	# Back to the panel: show the right order, and offer another try.
	var notes := ""
	if _round_fails >= 2 and ROUNDS[_round] - _length_cut > 2:
		_length_cut += 1
		_round_fails = 0
		_extra_show = 0.3
		notes = StoryText.FLASH_TEXT["fewer"]
	for i in _sequence.size():
		_set_card(i, "face", _sequence[i])
	_phase_label.text = StoryText.FLASH_TEXT["order_was"]
	_result_label.add_theme_color_override("font_color", WRONG_COLOR)
	_result_label.text = notes
	var back := create_tween().set_parallel()
	back.tween_property(_panel, "modulate:a", 1.0, 0.25)
	back.tween_property(_dim, "color:a", 0.6, 0.25)
	back.tween_property(_speech, "modulate:a", 0.0, 0.25)
	_again_button.show()
	_again_button.grab_focus()
	_state = "failed"
	print("[Minigame] try again ready")

func _on_again() -> void:
	if _state != "failed":
		return
	_topple_hermes(false)
	_start_round()

## Lays Hermes on his back, or stands him up again.
func _topple_hermes(down: bool) -> void:
	if hermes == null or not is_instance_valid(hermes):
		return
	var sprite := hermes.get_node_or_null("Sprite") as Node2D
	if sprite == null:
		return
	if down:
		_hermes_pose = {"rotation": sprite.rotation, "position": sprite.position}
		hermes.set_physics_process(false)
		var fall := create_tween().set_parallel()
		fall.tween_property(sprite, "rotation", -PI / 2.0, 0.28).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		fall.tween_property(sprite, "position", Vector2(4, 6), 0.28)
	elif not _hermes_pose.is_empty():
		sprite.rotation = _hermes_pose["rotation"]
		sprite.position = _hermes_pose["position"]
		_hermes_pose = {}
		hermes.set_physics_process(true)

func _shake_node(node: Control) -> void:
	var base := node.position
	var tween := create_tween()
	for offset in [Vector2(-9, 4), Vector2(8, -5), Vector2(-6, 3), Vector2(4, -2), Vector2.ZERO]:
		tween.tween_property(node, "position", base + offset, 0.06)

# ---------------------------------------------------------------- input

## Keys are handled here, before the buttons see them, so left / right always step one herb along
## the row in its current order and E / Enter always picks the herb in focus.
func _input(event: InputEvent) -> void:
	var accept := event.is_action_pressed("interact") or event.is_action_pressed("ui_accept")
	var step := 0
	if event.is_action_pressed("ui_right"):
		step = 1
	elif event.is_action_pressed("ui_left"):
		step = -1
	if not accept and step == 0:
		return
	get_viewport().set_input_as_handled()
	if _state == "failed":
		if accept:
			_on_again()
		return
	if _state != "repeat":
		return
	var focused := get_viewport().gui_get_focus_owner()
	var index := -1
	if focused is Button and _choices.has(focused):
		index = (focused as Button).get_index()
	if step != 0:
		var target := clampi(index + step, 0, _choices_row.get_child_count() - 1) if index >= 0 else 0
		(_choices_row.get_child(target) as Button).grab_focus()
		AudioController.play_sfx("ui_move")
	elif index >= 0:
		_on_choice(_choices_row.get_child(index).get_meta("herb"))
	else:
		(_choices_row.get_child(0) as Button).grab_focus()

func _exit_tree() -> void:
	_topple_hermes(false)

func _set_player_movement(enabled: bool) -> void:
	var player = get_tree().get_first_node_in_group("player")
	if player:
		player.set_controls_enabled(enabled)
