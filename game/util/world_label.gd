extends RefCounted
## Floating labels in the world (names, plot states, the interact prompt): small cream text with
## a dark outline, centred on their node. A label above its node grows upwards and one below it
## grows downwards, so a second line never spills onto the sprite it describes.

const FONT_SIZE := 11
const TEXT_COLOR := Color(1.0, 0.96, 0.86)
const OUTLINE_COLOR := Color(0.13, 0.08, 0.05, 0.95)
const WIDTH := 200.0
const HEIGHT := 40.0

## Places `label` with its last line ending at `edge_y` (local pixels) when `above`, or its first
## line starting there when not, centred on x = 0.
static func setup(label: Label, edge_y: float, above: bool = true, font_size: int = FONT_SIZE) -> void:
	var settings := LabelSettings.new()
	settings.font_size = font_size
	settings.font_color = TEXT_COLOR
	settings.outline_size = 4
	settings.outline_color = OUTLINE_COLOR
	label.label_settings = settings
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM if above else VERTICAL_ALIGNMENT_TOP
	label.size = Vector2(WIDTH, HEIGHT)
	label.position = Vector2(-WIDTH / 2.0, edge_y - HEIGHT if above else edge_y)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.z_index = 40
