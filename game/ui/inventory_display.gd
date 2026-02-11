extends CanvasLayer

var panel: PanelContainer
var items_container: VBoxContainer

var _item_names: Dictionary = {
	"moly_seed": "Moly Seeds",
	"moly": "Moly",
	"calming_draught": "Calming Draught",
}

var _item_colors: Dictionary = {
	"moly_seed": Color(0.7, 0.5, 0.2),
	"moly": Color(0.9, 0.9, 0.3),
	"calming_draught": Color(0.4, 0.6, 0.9),
}

func _ready() -> void:
	layer = 5
	_build_ui()
	GameState.inventory_changed.connect(_on_inventory_changed)
	_refresh()

func _build_ui() -> void:
	# Create panel container anchored to top-right
	panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(160, 0)

	# Position in top-right corner (CanvasLayer uses screen coords, not camera)
	panel.anchor_left = 1.0
	panel.anchor_right = 1.0
	panel.anchor_top = 0.0
	panel.anchor_bottom = 0.0
	panel.offset_left = -170  # 160 width + 10px margin
	panel.offset_right = -10
	panel.offset_top = 10
	panel.offset_bottom = 10
	panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN

	# Semi-transparent dark background
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.1, 0.1, 0.8)
	style.border_width_left = 2
	style.border_width_right = 2
	style.border_width_top = 2
	style.border_width_bottom = 2
	style.border_color = Color(0.3, 0.3, 0.3, 0.9)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 8
	style.content_margin_bottom = 8
	panel.add_theme_stylebox_override("panel", style)

	add_child(panel)

	# Main VBox container
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	panel.add_child(vbox)

	# Title label
	var title = Label.new()
	title.text = "Inventory"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))
	vbox.add_child(title)

	# Separator
	var separator = HSeparator.new()
	separator.add_theme_constant_override("separation", 4)
	vbox.add_child(separator)

	# Items container
	items_container = VBoxContainer.new()
	items_container.add_theme_constant_override("separation", 4)
	vbox.add_child(items_container)

func _on_inventory_changed(_item_id: String, _qty: int) -> void:
	_refresh()

func _refresh() -> void:
	# Clear existing item displays
	for child in items_container.get_children():
		child.queue_free()

	# Get all items from inventory
	var has_items = false
	for item_id in GameState.inventory:
		var quantity = GameState.inventory[item_id]
		if quantity > 0:
			has_items = true
			_add_item_row(item_id, quantity)

	# Show/hide panel based on inventory state
	panel.visible = has_items

func _add_item_row(item_id: String, quantity: int) -> void:
	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 6)

	# Color square indicator
	var color_rect = ColorRect.new()
	color_rect.custom_minimum_size = Vector2(12, 12)
	color_rect.color = _item_colors.get(item_id, Color.WHITE)
	hbox.add_child(color_rect)

	# Item name and quantity
	var label = Label.new()
	var display_name = _item_names.get(item_id, item_id)
	label.text = "%s x%d" % [display_name, quantity]
	label.add_theme_font_size_override("font_size", 14)
	label.add_theme_color_override("font_color", Color(0.95, 0.95, 0.95))
	hbox.add_child(label)

	items_container.add_child(hbox)
