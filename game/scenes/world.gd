extends Node2D
## The one world scene: Aiaia at the top, the cove at the bottom. Ground, props and
## collision come from game/data/world_map.gd; the entities are placed in world.tscn.

const PLAYER_SCENE := preload("res://game/entities/player/player.tscn")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const WorldMapData := preload("res://game/data/world_map.gd")
const AIAIA_SPAWN := Vector2(270, 350)
const CREDITS_SCENE := "res://game/scenes/credits.tscn"
const PARTICLE_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/ui/particle_soft.png"
const TILE_SIZE: int = WorldMapData.TILE
## A ground cell value packs the atlas and tile: atlas_index * 10000 + ty * 100 + tx.
const CELL_ATLAS_STRIDE := 10000
const CELL_ROW_STRIDE := 100
const BUTTERFLY_SCRIPT := preload("res://game/entities/ambient/butterfly.gd")
const GroundShadow := preload("res://game/util/ground_shadow.gd")
## [position, wing colour]: pale yellow, white and lilac, the colours of the flowers in the paintings.
const BUTTERFLIES := [
	[Vector2(112, 560), Color(0.98, 0.93, 0.62)],
	[Vector2(432, 556), Color(0.96, 0.96, 0.98)],
	[Vector2(340, 170), Color(0.82, 0.72, 0.95)],
	[Vector2(400, 420), Color(0.98, 0.93, 0.62)],
	[Vector2(150, 930), Color(0.96, 0.96, 0.98)],
]

var _ending_transition_started: bool = false

func _ready() -> void:
	_setup_gradient_backgrounds()
	_build_tileset_visuals()

	y_sort_enabled = true
	var player := PLAYER_SCENE.instantiate()
	player.global_position = AIAIA_SPAWN
	add_child(player)
	var camera := $Camera2D
	camera.reparent(player, false)

	GameState.flag_changed.connect(_on_flag_changed)

	AudioController.play_music("world")
	_setup_ambience()

func _setup_ambience() -> void:
	# Drifting pollen over the island. The cove's mist drifts in banks (strait.gd): soft particles
	# blown up to mist size showed as dark smudges in the browser build.
	var soft: Texture2D = TextureLoaderUtil.load_texture(PARTICLE_TEXTURE_PATH)
	var pollen := CPUParticles2D.new()
	pollen.name = "Pollen"
	pollen.texture = soft
	pollen.amount = 48
	pollen.lifetime = 7.0
	pollen.preprocess = 6.0
	pollen.position = Vector2(272, 720)
	pollen.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	pollen.emission_rect_extents = Vector2(272, 720)
	pollen.direction = Vector2(1, -0.3)
	pollen.spread = 40.0
	pollen.gravity = Vector2(0, -3)
	pollen.initial_velocity_min = 4.0
	pollen.initial_velocity_max = 12.0
	pollen.scale_amount_min = 0.15
	pollen.scale_amount_max = 0.3
	pollen.color = Color(1.0, 0.95, 0.7, 0.55)
	pollen.z_index = 6
	add_child(pollen)

	# A few butterflies over the flower beds, the terrace and the well. None in the cove.
	for spot in BUTTERFLIES:
		var butterfly: Node2D = BUTTERFLY_SCRIPT.new()
		butterfly.name = "Butterfly%d" % get_child_count()
		butterfly.position = spot[0]
		butterfly.wing_color = spot[1]
		add_child(butterfly)

func _setup_gradient_backgrounds() -> void:
	_replace_with_gradient($AiaiaBackground, Color(0.7, 0.85, 0.4), Color(0.35, 0.55, 0.25))
	_replace_with_gradient($ScyllaBackground, Color(0.25, 0.3, 0.45), Color(0.08, 0.1, 0.15))

func _replace_with_gradient(color_rect: ColorRect, top_color: Color, bottom_color: Color) -> void:
	var tex_rect := TextureRect.new()
	tex_rect.texture = TextureLoaderUtil.vertical_gradient(top_color, bottom_color)
	tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
	tex_rect.position = color_rect.position
	tex_rect.size = color_rect.size
	tex_rect.z_index = -30  # under the tile floor, which is at -20

	color_rect.add_sibling(tex_rect)
	move_child(tex_rect, color_rect.get_index())
	color_rect.queue_free()

func _build_tileset_visuals() -> void:
	var tile_layer: Node2D = $TileVisualLayer
	tile_layer.z_index = -20
	var textures: Array = []
	for path in WorldMapData.ATLASES:
		textures.append(TextureLoaderUtil.load_texture(path))

	var tile_set := TileSet.new()
	tile_set.tile_size = Vector2i(TILE_SIZE, TILE_SIZE)
	var source_ids: Array[int] = []
	for texture in textures:
		var source := TileSetAtlasSource.new()
		source.texture = texture
		source.texture_region_size = Vector2i(TILE_SIZE, TILE_SIZE)
		if texture != null:
			for tx in int(texture.get_width() / TILE_SIZE):
				for ty in int(texture.get_height() / TILE_SIZE):
					source.create_tile(Vector2i(tx, ty))
		source_ids.append(tile_set.add_source(source))

	var total := 0
	for layer_data in [WorldMapData.GROUND_ROWS, WorldMapData.OVERLAY_ROWS]:
		var layer := TileMapLayer.new()
		layer.name = "Ground" if total == 0 else "Overlay"
		layer.tile_set = tile_set
		layer.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		tile_layer.add_child(layer)
		for row in layer_data.size():
			var cells: Array = layer_data[row]
			for col in cells.size():
				var v: int = cells[col]
				if v < 0:
					continue
				var atlas_index: int = v / CELL_ATLAS_STRIDE
				var tile: int = v % CELL_ATLAS_STRIDE
				layer.set_cell(Vector2i(col, row), source_ids[atlas_index],
						Vector2i(tile % CELL_ROW_STRIDE, tile / CELL_ROW_STRIDE))
		total += layer.get_used_cells().size()

	print("[World] ground tiles: %d, sources: %d" % [total, tile_set.get_source_count()])
	_build_decor(textures)
	_build_blockers()

func _build_decor(textures: Array) -> void:
	# Props are direct children so the world's y-sort draws them in front of or behind Circe.
	for d in WorldMapData.DECOR:
		var texture: Texture2D = textures[d[0]]
		if texture == null:
			continue
		var atlas := AtlasTexture.new()
		atlas.atlas = texture
		atlas.region = Rect2(d[1] * TILE_SIZE, d[2] * TILE_SIZE, d[3] * TILE_SIZE, d[4] * TILE_SIZE)
		var sprite := Sprite2D.new()
		sprite.texture = atlas
		sprite.centered = false
		sprite.offset = Vector2(0, -d[4] * TILE_SIZE)
		sprite.position = Vector2(d[5] * TILE_SIZE, (d[6] + d[4]) * TILE_SIZE)
		add_child(sprite)
		if d.size() > 8 and d[7] > 0:
			GroundShadow.attach(sprite, Vector2(d[3] * TILE_SIZE / 2.0, -3.0), Vector2(d[7], d[8]))

func _build_blockers() -> void:
	var body := StaticBody2D.new()
	body.name = "Blockers"
	body.collision_layer = 1
	body.collision_mask = 0
	for r in WorldMapData.BLOCKED:
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = Vector2(r[2], r[3])
		shape.shape = rect
		shape.position = Vector2(r[0] + r[2] / 2.0, r[1] + r[3] / 2.0)
		body.add_child(shape)
	add_child(body)

func _on_flag_changed(flag: String, value: bool) -> void:
	if flag != "game_complete" or not value or _ending_transition_started:
		return

	_ending_transition_started = true
	# Small pause lets the last dialogue line land before transitioning.
	await get_tree().create_timer(0.6).timeout
	SceneManager.change_scene(CREDITS_SCENE)
