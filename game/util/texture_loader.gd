extends RefCounted

class_name TextureLoader

static func load_texture(resource_path: String) -> Texture2D:
	var absolute_path := ProjectSettings.globalize_path(resource_path)
	if not FileAccess.file_exists(absolute_path):
		push_warning("Texture file does not exist: %s" % resource_path)
		return null

	var image := Image.new()
	if image.load(absolute_path) != OK:
		push_warning("Failed to load texture from path: %s" % resource_path)
		return null

	return ImageTexture.create_from_image(image)
