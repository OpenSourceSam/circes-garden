extends CanvasLayer
## The panel in the top-left corner: the current day and the current quest goal, updated as flags change.

const UiStyle := preload("res://game/ui/ui_style.gd")
const StoryText := preload("res://game/data/story_text.gd")

var panel: PanelContainer
var day_label: Label
var quest_label: Label

var _quest_texts: Dictionary = StoryText.QUEST_TITLES.duplicate(true)

func _ready() -> void:
	layer = 5
	_build_ui()
	GameState.flag_changed.connect(_on_flag_changed)
	GameState.day_advanced.connect(_on_day_advanced)
	_refresh()

func _build_ui() -> void:
	# Create panel container anchored to top-left
	panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(250, 0)

	# Position in top-left corner (CanvasLayer uses screen coords)
	panel.anchor_left = 0.0
	panel.anchor_right = 0.0
	panel.anchor_top = 0.0
	panel.anchor_bottom = 0.0
	panel.offset_left = 10
	panel.offset_right = 260
	panel.offset_top = 10
	panel.offset_bottom = 10
	panel.grow_horizontal = Control.GROW_DIRECTION_END

	var style := UiStyle.panel(10, 8)
	panel.add_theme_stylebox_override("panel", style)

	add_child(panel)

	# Main VBox container
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	panel.add_child(vbox)

	# Day label
	day_label = Label.new()
	day_label.text = "Day 1"
	day_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	day_label.add_theme_font_size_override("font_size", 15)
	day_label.add_theme_color_override("font_color", UiStyle.GOLD_TEXT)
	vbox.add_child(day_label)

	# Separator
	var separator = HSeparator.new()
	separator.add_theme_constant_override("separation", 4)
	vbox.add_child(separator)

	# Quest objective label
	quest_label = Label.new()
	quest_label.text = "No active quest"
	quest_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	quest_label.add_theme_font_size_override("font_size", 14)
	quest_label.add_theme_color_override("font_color", UiStyle.TEXT)
	vbox.add_child(quest_label)

func _on_flag_changed(_flag: String, _value: bool) -> void:
	_refresh()

func _on_day_advanced(_new_day: int) -> void:
	_refresh()

func _refresh() -> void:
	# Update day counter
	day_label.text = "Day %d" % GameState.current_day

	# Find active quest (check in reverse order - latest quest wins)
	var quest_text = "No active quest"
	var quest_order = [
		"game_complete",
		"quest_5_active",
		"quest_4_active",
		"quest_3_active",
		"quest_2_active",
		"quest_1_active",
	]

	for quest_flag in quest_order:
		if GameState.get_flag(quest_flag):
			quest_text = _quest_texts.get(quest_flag, "Unknown quest")
			break

	quest_label.text = quest_text
