extends RefCounted
## The one look for every panel (dialogue, quest, inventory, herb lesson): dark walnut with a
## thin gilt border and soft rounded corners, so the interface reads as one hand-made set.

const BG := Color(0.11, 0.08, 0.06, 0.9)
const BORDER := Color(0.78, 0.62, 0.36, 1.0)
const GOLD_TEXT := Color(0.95, 0.82, 0.52)
const TEXT := Color(1.0, 0.97, 0.9)

static func panel(margin_x: int = 10, margin_y: int = 8, border: int = 2) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = BG
	style.border_color = BORDER
	style.set_border_width_all(border)
	style.set_corner_radius_all(6)
	style.shadow_color = Color(0, 0, 0, 0.4)
	style.shadow_size = 4
	style.content_margin_left = margin_x
	style.content_margin_right = margin_x
	style.content_margin_top = margin_y
	style.content_margin_bottom = margin_y
	return style
