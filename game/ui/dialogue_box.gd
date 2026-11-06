extends CanvasLayer
## The dialogue panel at the bottom of the screen: speaker portrait, name and typewriter text.
## Entities start dialogue through open(); the box pauses the player until the last line.

signal dialogue_ended(dialogue_id: String)
## Each line as it appears, so a scene can act on a moment inside a conversation.
signal line_shown(dialogue_id: String, text: String)
## A line's "cue" (story_text.gd), when it has one: what the scene should act out on that line.
signal line_cue(dialogue_id: String, cue: String)

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const StoryText := preload("res://game/data/story_text.gd")
const UiStyle := preload("res://game/ui/ui_style.gd")
const PORTRAITS := {
	"Circe": "res://assets/image_pipeline/generated/raw/sprites/characters/circe/circe_idle.png",
	"Hermes": "res://assets/image_pipeline/generated/raw/sprites/characters/hermes/hermes_idle.png",
}
## Head and shoulders of the first (standing, facing down) frame of a 64-px character sheet.
const PORTRAIT_REGION := Rect2(16, 10, 32, 32)
const CHARS_PER_SECOND := 55.0
const MAX_BOX_WIDTH := 900.0
const BOX_HEIGHT := 230.0

var panel: PanelContainer
var portrait: TextureRect
var speaker_label: Label
var dialogue_label: RichTextLabel

var _current_dialogue: DialogueData = null
var _current_line_index: int = 0
var _is_active: bool = false
var _typing: bool = false
var _type_progress: float = 0.0

## Starts dialogue `id` on the scene's dialogue box, with `lines` or else StoryText.LINES[id].
## Returns the box, or null when the scene has none or a dialogue is already open.
static func open(context: Node, id: String, lines: Array = []) -> CanvasLayer:
	var box = context.get_tree().get_first_node_in_group("dialogue_box")
	if box == null or box.is_active():
		return null
	var dialogue := DialogueData.new()
	dialogue.id = id
	dialogue.lines = (lines if not lines.is_empty() else StoryText.LINES[id]).duplicate(true)
	box.start_dialogue(dialogue)
	return box

func _ready() -> void:
	add_to_group("dialogue_box")
	_build_ui()
	panel.hide()

func _build_ui() -> void:
	panel = PanelContainer.new()
	panel.name = "Panel"
	panel.add_theme_stylebox_override("panel", _panel_style())
	add_child(panel)

	# Bottom-centre, never wider than the portrait screen allows.
	panel.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	var viewport_width := get_viewport().get_visible_rect().size.x
	var box_width := minf(viewport_width - 100.0, MAX_BOX_WIDTH)
	panel.offset_left = (viewport_width - box_width) / 2.0
	panel.offset_right = -panel.offset_left   # right edge is anchored to the screen's right side
	panel.offset_bottom = -30
	panel.offset_top = panel.offset_bottom - BOX_HEIGHT

	var row := HBoxContainer.new()
	row.name = "Row"
	row.add_theme_constant_override("separation", 16)
	panel.add_child(row)

	portrait = TextureRect.new()
	portrait.name = "Portrait"
	portrait.custom_minimum_size = Vector2(128, 128)
	portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	portrait.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	row.add_child(portrait)
	row.add_child(_build_text_column())

func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.11, 0.08, 0.06, 1.0)
	style.border_color = Color(0.78, 0.62, 0.36, 1.0)
	style.set_border_width_all(3)
	style.set_corner_radius_all(6)
	style.shadow_color = Color(0, 0, 0, 0.45)
	style.shadow_size = 6
	style.content_margin_left = 20
	style.content_margin_right = 20
	style.content_margin_top = 15
	style.content_margin_bottom = 15
	return style

func _build_text_column() -> VBoxContainer:
	var column := VBoxContainer.new()
	column.name = "VBox"
	column.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	speaker_label = Label.new()
	speaker_label.name = "SpeakerLabel"
	speaker_label.add_theme_font_override("font", UiStyle.TITLE_FONT)
	speaker_label.add_theme_font_size_override("font_size", 24)
	speaker_label.add_theme_color_override("font_color", Color(0.9, 0.8, 0.6, 1.0))
	column.add_child(speaker_label)

	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 5)
	column.add_child(spacer)

	dialogue_label = RichTextLabel.new()
	dialogue_label.name = "DialogueLabel"
	dialogue_label.bbcode_enabled = true
	dialogue_label.fit_content = true
	dialogue_label.scroll_active = false
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.add_theme_font_size_override("normal_font_size", 23)
	dialogue_label.add_theme_font_size_override("italics_font_size", 23)
	dialogue_label.add_theme_font_override("italics_font", UiStyle.ITALIC_FONT)
	dialogue_label.add_theme_color_override("default_color", Color(1, 0.97, 0.9, 1))
	dialogue_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dialogue_label.custom_minimum_size = Vector2(0, 80)
	column.add_child(dialogue_label)

	var continue_prompt := Label.new()
	continue_prompt.name = "ContinuePrompt"
	continue_prompt.text = "Enter  continue"
	continue_prompt.size_flags_horizontal = Control.SIZE_SHRINK_END
	continue_prompt.add_theme_font_size_override("font_size", 16)
	continue_prompt.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7, 1.0))
	column.add_child(continue_prompt)
	return column

func _unhandled_input(event: InputEvent) -> void:
	if not _is_active:
		return
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		advance()
		get_viewport().set_input_as_handled()

func start_dialogue(dialogue: DialogueData) -> void:
	_current_dialogue = dialogue
	_current_line_index = 0
	_is_active = true
	print("[Dialogue] start %s" % dialogue.id)
	panel.show()
	AudioController.play_sfx("ui_open")
	_display_current_line()
	_set_player_active(false)

func advance() -> void:
	if _typing:
		# First press shows the whole line; the next press moves on.
		_typing = false
		dialogue_label.visible_characters = -1
		return
	AudioController.play_sfx("ui_move")
	_current_line_index += 1
	if _current_line_index >= _current_dialogue.lines.size():
		end_dialogue()
	else:
		_display_current_line()

func _display_current_line() -> void:
	var line: Dictionary = _current_dialogue.lines[_current_line_index]
	var speaker: String = line.get("speaker", "")
	var text: String = line.get("text", "")
	speaker_label.text = speaker
	dialogue_label.text = _to_bbcode(text)
	dialogue_label.visible_characters = 0
	_type_progress = 0.0
	_typing = true
	_set_portrait(speaker)
	line_shown.emit(_current_dialogue.id, text)
	var cue: String = line.get("cue", "")
	if cue != "":
		line_cue.emit(_current_dialogue.id, cue)
	var lower := text.to_lower()
	if "scream" in lower or "shriek" in lower:
		SceneManager.shake_camera(0.7, 8.0)

func _process(delta: float) -> void:
	if not _typing:
		return
	_type_progress += delta * CHARS_PER_SECOND
	var total := dialogue_label.get_total_character_count()
	var shown := mini(int(_type_progress), total)
	dialogue_label.visible_characters = shown
	if shown >= total:
		_typing = false
		dialogue_label.visible_characters = -1

## Story text marks narration and stage directions with *asterisks*; they show as soft italics.
static func _to_bbcode(text: String) -> String:
	var out := text.replace("[", "[lb]")
	var regex := RegEx.new()
	regex.compile("\\*([^*]+)\\*")
	return regex.sub(out, "[i][color=#e8d9b8]$1[/color][/i]", true)

func _set_portrait(speaker: String) -> void:
	var sheet: Texture2D = null
	if PORTRAITS.has(speaker):
		sheet = TextureLoaderUtil.load_texture(PORTRAITS[speaker])
	if sheet == null:
		portrait.visible = false
		return
	var atlas := AtlasTexture.new()
	atlas.atlas = sheet
	atlas.region = PORTRAIT_REGION
	portrait.texture = atlas
	portrait.visible = true

func end_dialogue() -> void:
	var dialogue_id := _current_dialogue.id
	print("[Dialogue] end %s" % dialogue_id)
	_current_dialogue = null
	_is_active = false
	AudioController.play_sfx("ui_close")
	panel.hide()
	_set_player_active(true)
	dialogue_ended.emit(dialogue_id)

## Stops Circe walking and interacting while a dialogue is open.
func _set_player_active(enabled: bool) -> void:
	var player := get_tree().get_first_node_in_group("player")
	if player:
		player.set_controls_enabled(enabled)

func is_active() -> bool:
	return _is_active
