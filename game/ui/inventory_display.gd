extends CanvasLayer
## The inventory panel in the top-right corner: an icon, name and count for each item Circe carries.

const UiStyle := preload("res://game/ui/ui_style.gd")
const TextureLoaderUtil = preload("res://game/util/texture_loader.gd")

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

var _item_icon_paths: Dictionary = {
	"moly_seed": "res://assets/image_pipeline/generated/raw/sprites/ui/icon_moly_seed.png",
	"moly": "res://assets/image_pipeline/generated/raw/sprites/ui/icon_moly.png",
	"calming_draught": "res://assets/image_pipeline/generated/raw/sprites/ui/icon_calming_draught.png",
}

var _icon_cache: Dictionary = {}

func _ready() -> void:
	layer = 5
	_build_ui()
	_build_icon_cache()
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

	var style := UiStyle.panel(8, 8)
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
	title.add_theme_color_override("font_color", UiStyle.GOLD_TEXT)
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

	var icon_texture: Texture2D = _icon_cache.get(item_id)
	if icon_texture:
		var icon = TextureRect.new()
		icon.custom_minimum_size = Vector2(18, 18)
		icon.texture = icon_texture
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		hbox.add_child(icon)
	else:
		# Fallback while icon set is incomplete.
		var color_rect = ColorRect.new()
		color_rect.custom_minimum_size = Vector2(12, 12)
		color_rect.color = _item_colors.get(item_id, Color.WHITE)
		hbox.add_child(color_rect)

	# Item name and quantity
	var label = Label.new()
	var display_name = _item_names.get(item_id, item_id)
	label.text = "%s x%d" % [display_name, quantity]
	label.add_theme_font_size_override("font_size", 14)
	label.add_theme_color_override("font_color", UiStyle.TEXT)
	hbox.add_child(label)

	items_container.add_child(hbox)

func _build_icon_cache() -> void:
	for item_id in _item_icon_paths.keys():
		var texture: Texture2D = TextureLoaderUtil.load_texture(_item_icon_paths[item_id])
		_icon_cache[item_id] = _trim_texture(texture)

func _trim_texture(texture: Texture2D) -> Texture2D:
	if texture == null:
		return null

	var image := texture.get_image()
	if image == null:
		return texture

	var used_rect := image.get_used_rect()
	if used_rect.size == Vector2i.ZERO:
		return texture

	var atlas := AtlasTexture.new()
	atlas.atlas = texture
	atlas.region = Rect2(used_rect.position, used_rect.size)
	return atlas
