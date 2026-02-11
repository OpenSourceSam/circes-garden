extends Node2D

const PLAYER_SCENE := preload("res://game/entities/player/player.tscn")
const AIAIA_SPAWN := Vector2(270, 350)

func _ready() -> void:
	_setup_gradient_backgrounds()

	var player := PLAYER_SCENE.instantiate()
	player.global_position = AIAIA_SPAWN
	add_child(player)
	var camera := $Camera2D
	camera.reparent(player, false)

	# Connect to GameState for quest auto-completion
	GameState.inventory_changed.connect(_on_inventory_changed)

	AudioController.play_music("world")

func _setup_gradient_backgrounds() -> void:
	# Replace flat ColorRects with gradient TextureRects
	_apply_gradient($AiaiaBackground,
		Color(0.7, 0.85, 0.4),   # sunny green-gold (top)
		Color(0.35, 0.55, 0.25)) # earthy green (bottom)
	_apply_gradient($ScyllaBackground,
		Color(0.25, 0.3, 0.45),  # twilight blue (top)
		Color(0.08, 0.1, 0.15))  # deep sea (bottom)

func _apply_gradient(color_rect: ColorRect, top_color: Color, bottom_color: Color) -> void:
	var gradient := Gradient.new()
	gradient.set_color(0, top_color)
	gradient.set_color(1, bottom_color)

	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0.5, 0.0)  # top center
	texture.fill_to = Vector2(0.5, 1.0)    # bottom center
	texture.width = 2   # small texture, stretched
	texture.height = 64  # enough for smooth gradient

	var tex_rect := TextureRect.new()
	tex_rect.texture = texture
	tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
	tex_rect.position = color_rect.position
	tex_rect.size = color_rect.size

	# Insert gradient behind the ColorRect, then remove the ColorRect
	color_rect.add_sibling(tex_rect)
	move_child(tex_rect, color_rect.get_index())
	color_rect.queue_free()

func _on_inventory_changed(item_id: String, _new_quantity: int) -> void:
	# Quest 2 auto-complete: when player has 3+ moly
	if item_id == "moly" and GameState.get_flag("quest_2_active"):
		if GameState.get_item_count("moly") >= 3:
			GameState.set_flag("quest_2_complete", true)
			GameState.set_flag("quest_2_active", false)
			GameState.set_flag("quest_3_active", true)
