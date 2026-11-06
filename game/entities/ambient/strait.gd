extends Node2D
## Scylla's strait around her: the cliff face behind her, Charybdis turning across the water and
## banks of mist drifting over it all (art from tools/pixelart/cove_scene.py). The cliff and the
## whirlpool lie under everyone; some mist lies against the cliff behind Scylla and some drifts
## in front of her heads. roar() is the cue for "Mist fills the strait. Across the water, the
## whirlpool roars.": the whirlpool spins faster and the mist thickens for a while.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const CLIFF_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/cove_cliff.png"
const WHIRLPOOL_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/whirlpool.png"
const MIST_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/mist_banks.png"
const CLIFF_AT := Vector2(0, 2056)
const WHIRLPOOL_AT := Vector2(96, 2404)
const WHIRLPOOL_FRAMES := 8
const WHIRLPOOL_FPS := 9.0
const MAP_WIDTH := 544.0
## The strips in mist_banks.png, top to bottom: [y, width, height].
const MIST_STRIPS := [[0, 420, 30], [30, 300, 22], [52, 480, 40]]
## Drifting banks: [strip, world x, world y, speed in px/s, opacity, z_index]. z -4 lies between
## the cliff (-5) and Scylla (1); z 6 drifts in front of her heads. None comes down to the point,
## so Circe is never veiled.
const BANKS := [
	[2, 40.0, 2060.0, 4.0, 0.42, -4],
	[0, 300.0, 2096.0, -2.5, 0.30, -4],
	[2, 160.0, 2286.0, -3.0, 0.34, -4],
	[1, 20.0, 2150.0, 6.0, 0.34, 6],
	[0, 260.0, 2104.0, -5.0, 0.30, 6],
	[1, 380.0, 2226.0, 3.5, 0.26, 6],
	[0, -120.0, 2318.0, 2.5, 0.20, 6],
]
const ROAR_MIST := 1.7
const ROAR_SPIN := 2.2

var _whirlpool: Sprite2D
var _banks: Array[Sprite2D] = []
var _bank_x: Array[float] = []
var _time := 0.0
var _spin := 1.0
var _frame_time := 0.0

func _ready() -> void:
	add_to_group("strait")
	var cliff := Sprite2D.new()
	cliff.name = "Cliff"
	cliff.texture = TextureLoaderUtil.load_texture(CLIFF_PATH)
	cliff.centered = false
	cliff.position = CLIFF_AT
	cliff.z_index = -5
	add_child(cliff)

	_whirlpool = Sprite2D.new()
	_whirlpool.name = "Whirlpool"
	_whirlpool.texture = TextureLoaderUtil.load_texture(WHIRLPOOL_PATH)
	_whirlpool.hframes = WHIRLPOOL_FRAMES
	_whirlpool.position = WHIRLPOOL_AT
	_whirlpool.z_index = -5
	add_child(_whirlpool)

	var mist := TextureLoaderUtil.load_texture(MIST_PATH)
	for bank in BANKS:
		var strip: Array = MIST_STRIPS[bank[0]]
		var atlas := AtlasTexture.new()
		atlas.atlas = mist
		atlas.region = Rect2(0, strip[0], strip[1], strip[2])
		var sprite := Sprite2D.new()
		sprite.name = "Mist%d" % _banks.size()
		sprite.texture = atlas
		sprite.centered = false
		sprite.position = Vector2(bank[1], bank[2])
		sprite.modulate = Color(1, 1, 1, bank[4])
		sprite.z_index = bank[5]
		add_child(sprite)
		_banks.append(sprite)
		_bank_x.append(bank[1])

func _process(delta: float) -> void:
	_time += delta
	_frame_time += delta * _spin
	_whirlpool.frame = int(_frame_time * WHIRLPOOL_FPS) % WHIRLPOOL_FRAMES
	for i in _banks.size():
		var bank: Array = BANKS[i]
		var width: float = MIST_STRIPS[bank[0]][1]
		_bank_x[i] += bank[3] * delta
		# Wrap round once a bank has drifted wholly off one side of the map.
		if _bank_x[i] > MAP_WIDTH:
			_bank_x[i] -= MAP_WIDTH + width
		elif _bank_x[i] < -width:
			_bank_x[i] += MAP_WIDTH + width
		var bob := sin(_time * 0.4 + i * 1.7) * 3.0
		_banks[i].position = Vector2(_bank_x[i], bank[2] + bob).round()

func roar() -> void:
	var tween := create_tween().set_parallel(true)
	tween.tween_property(self, "_spin", ROAR_SPIN, 1.0)
	for i in _banks.size():
		var opacity: float = BANKS[i][4]
		tween.tween_property(_banks[i], "modulate:a", minf(opacity * ROAR_MIST, 0.6), 2.0)
	# It settles again long after she has turned back to the sea.
	var settle := create_tween().set_parallel(true)
	settle.tween_interval(25.0)
	settle.chain().tween_property(self, "_spin", 1.0, 4.0)
	for i in _banks.size():
		settle.parallel().tween_property(_banks[i], "modulate:a", BANKS[i][4], 6.0)
