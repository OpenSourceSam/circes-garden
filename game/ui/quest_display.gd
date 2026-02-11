extends CanvasLayer

var panel: PanelContainer
var day_label: Label
var quest_label: Label

var _quest_texts: Dictionary = {
	"game_complete": "You found peace.",
	"quest_5_active": "Return to Aiaia",
	"quest_4_active": "Sail to Scylla and use the potion",
	"quest_3_active": "Craft the Calming Draught (3 moly)",
	"quest_2_active": "Farm moly herbs in the garden",
	"quest_1_active": "Meet Hermes and learn about pharmaka",
}

func _ready() -> void:
	layer = 5
	_build_ui()
	GameState.flag_changed.connect(_on_flag_changed)
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

	# Semi-transparent dark background
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.1, 0.1, 0.8)
	style.border_width_left = 2
	style.border_width_right = 2
	style.border_width_top = 2
	style.border_width_bottom = 2
	style.border_color = Color(0.3, 0.3, 0.3, 0.9)
	style.content_margin_left = 10
	style.content_margin_right = 10
	style.content_margin_top = 8
	style.content_margin_bottom = 8
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
	day_label.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5))
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
	quest_label.add_theme_color_override("font_color", Color(0.95, 0.95, 0.95))
	vbox.add_child(quest_label)

func _on_flag_changed(_flag: String, _value: bool) -> void:
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
