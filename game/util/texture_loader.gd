extends RefCounted
## Small texture helpers shared by the UI and scenes.

class_name TextureLoader

## Loads a texture through Godot's resource system so it works in the editor
## and in exported builds (web, Windows, Android). Image.load() on an OS path only
## worked in the editor because exports do not contain the source PNGs.
static func load_texture(resource_path: String) -> Texture2D:
	if not ResourceLoader.exists(resource_path):
		push_warning("Texture resource does not exist: %s" % resource_path)
		return null

	var texture := load(resource_path) as Texture2D
	if texture == null:
		push_warning("Failed to load texture from path: %s" % resource_path)
	return texture

## A top-to-bottom two-colour gradient, for TextureRects set to STRETCH_SCALE.
static func vertical_gradient(top_color: Color, bottom_color: Color) -> GradientTexture2D:
	var gradient := Gradient.new()
	gradient.set_color(0, top_color)
	gradient.set_color(1, bottom_color)
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0.5, 0.0)
	texture.fill_to = Vector2(0.5, 1.0)
	texture.width = 2
	texture.height = 64
	return texture
