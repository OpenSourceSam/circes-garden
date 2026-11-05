extends RefCounted
## Turns this game's sprite sheets into SpriteFrames animations. A sheet is a grid of
## equal cells: one row per facing, one column per frame
## (assets/image_pipeline/docs/ASSET_SPEC.md).

const FOUR_WAY_ROWS := {"down": 0, "up": 1, "left": 2, "right": 3}
const SIDE_ROWS := {"left": 0, "right": 1}

## Adds one looping "<action>_<facing>" animation per entry in rows ({facing: row index}).
## A missing texture adds nothing, so a broken path shows as an invisible sprite, not a crash.
static func add_animations(frames: SpriteFrames, action: String, texture: Texture2D,
		rows: Dictionary, fps: float, columns: int = 4) -> void:
	if texture == null:
		return
	var cell := Vector2(texture.get_width() / columns, texture.get_height() / rows.size())
	for facing in rows:
		var animation_name := "%s_%s" % [action, facing]
		frames.add_animation(animation_name)
		frames.set_animation_loop(animation_name, true)
		frames.set_animation_speed(animation_name, fps)
		var row: int = rows[facing]
		for column in columns:
			var atlas := AtlasTexture.new()
			atlas.atlas = texture
			atlas.region = Rect2(Vector2(column * cell.x, row * cell.y), cell)
			frames.add_frame(animation_name, atlas)

## The facing ("left", "right", "up", "down") for the larger axis of a direction.
static func facing_from(direction: Vector2) -> String:
	if absf(direction.x) > absf(direction.y):
		return "right" if direction.x > 0.0 else "left"
	return "down" if direction.y > 0.0 else "up"
