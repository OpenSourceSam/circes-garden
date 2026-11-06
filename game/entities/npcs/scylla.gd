extends StaticBody2D
## Scylla in her strait: her back out of the water and six dog heads on necks longer than masts.
## She is drawn every frame from the parts in scylla_parts.png (tools/pixelart/scylla_big.py):
## each neck is a chain of overlapping discs on a curve from her back to its head, at whole
## pixels and 1:1 scale. Lines of her scenes carry cues (story_text.gd) that she acts out: she
## comes down out of the fog, snaps up the vial, goes still, wakes, strikes the rock beside
## Circe and turns back to the sea. With the Calming Draught Circe tries the cure, and it fails,
## as in the novel. Circe only ever stands south of her, so she never overlaps Circe.

const Parts := preload("res://game/data/scylla_parts.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const WorldLabel := preload("res://game/util/world_label.gd")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")

## Outer necks first, so the middle ones overlap them.
const DRAW_ORDER := [0, 5, 1, 4, 2, 3]
## How far each neck bends sideways, in pixels, left to right.
const BULGE := [-26.0, -18.0, -8.0, 8.0, 18.0, 26.0]
## Head targets relative to the waterline (this node), [x, y, head sprite], left to right.
## "sea": high in the mist, watching for ships. "circe": down out of the fog, every eye on her.
const POSES := {
	"sea": [[-158, -238, "side_closed_l"], [-104, -292, "side_closed_l"], [-40, -318, "side_closed_l"],
			[36, -306, "side_closed_r"], [100, -276, "side_closed_r"], [156, -226, "side_closed_r"]],
	"circe": [[-150, -150, "front_closed"], [-98, -196, "front_closed"], [-36, -222, "front_closed"],
			[30, -214, "front_closed"], [90, -184, "front_closed"], [146, -146, "front_closed"]],
}
## How much each pose lets the heads drift and bob (1 = the full slow sway).
const SWAY := {"sea": 1.0, "circe": 0.45}
## The low rock right of the point (worldmap.py COVE_PROPS), in world pixels, and the head
## that strikes it. Circe can stand no further right on the point than x 312, so it misses her.
const STRIKE_AT := Vector2(352, 2450)
const STRIKER := 4
## The head that catches the vial.
const CATCHER := 2
## How fast a head closes on its target, per second: drifting, rearing back, lunging.
const FOLLOW := 2.6
const REAR := 7.0
const LUNGE := 30.0
## The top of the cove in the world (worldmap.py COVE_ROW0 * 32).
const COVE_TOP := 1984.0

@onready var label: Label = $Label

var _texture: Texture2D
var _parts := {}                        # part name -> [source Rect2, pivot Vector2]
var _seg := {}                          # "o", "f", "s", "b" -> Array indexed by radius
var _bases: Array[Vector2] = []
var _heads: Array[Vector2] = []         # where each head is now (local)
var _targets: Array[Vector2] = []       # where each head is going
var _follow: Array[float] = []
var _pinned: Array[bool] = []           # held exactly on its target, no drift (the strike)
var _open_until: Array[float] = []      # jaw open until this time
var _next_snap: Array[float] = []       # when an idle head next snaps at the air
var _chains: Array = []                 # per neck: Array of Vector3i (x, y, radius)
var _pose := "sea"
var _sway := 1.0
var _calm := false
var _striking := false
var _sequence := 0                      # bumps when a new cue starts, so old ones stop
var _time := 0.0
var _vial_visible := false
var _vial_pos := Vector2.ZERO
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	z_index = 1   # over the rocks in the strait
	WorldLabel.setup(label, 18.0, false)
	_rng.seed = 6
	_texture = TextureLoaderUtil.load_texture(Parts.TEXTURE)
	for part_name in Parts.REGIONS:
		var r: Array = Parts.REGIONS[part_name]
		_parts[part_name] = [Rect2(r[0], r[1], r[2], r[3]), Vector2(r[4], r[5])]
	for kind in ["o", "f", "s", "b"]:
		var by_radius: Array = []
		by_radius.resize(Parts.SEG_MAX + 1)
		for r in range(Parts.SEG_MIN, Parts.SEG_MAX + 1):
			by_radius[r] = _parts["seg_%s%d" % [kind, r]]
		_seg[kind] = by_radius
	for b in Parts.NECK_BASES:
		_bases.append(Vector2(b[0], b[1]))
	for i in 6:
		var target := _pose_target(i)
		_heads.append(target)
		_targets.append(target)
		_follow.append(FOLLOW)
		_pinned.append(false)
		_open_until.append(0.0)
		_next_snap.append(_rng.randf_range(1.0, 5.0))
		_chains.append([])

func prompt_text() -> String:
	return "Face Scylla" if GameState.get_flag("quest_4_active") else "Look at Scylla"

func world_label() -> Label:
	return label

func interact() -> void:
	# Listen before opening: the first line's cue fires as the box opens.
	var box := get_tree().get_first_node_in_group("dialogue_box")
	if box and not box.line_cue.is_connected(_on_line_cue):
		box.line_cue.connect(_on_line_cue)
	if not GameState.get_flag("quest_4_active"):
		DialogueBox.open(self, "scylla_not_ready")
	elif GameState.give_draught_to_scylla():
		DialogueBox.open(self, "scylla_cure_attempt")
		label.text = "Scylla\n(unchanged)"
	else:
		DialogueBox.open(self, "scylla_no_potion")

# ---------------------------------------------------------------------------
# Motion

func _pose_target(i: int) -> Vector2:
	var p: Array = POSES[_pose][i]
	return Vector2(p[0], p[1])

## Slow drift plus a quicker bob, different for every head, so the six never move as one.
func _drift(i: int) -> Vector2:
	var t := _time
	return Vector2(sin(t * 0.37 + i * 1.9) * 14.0 + sin(t * 1.3 + i) * 3.0,
			sin(t * 0.29 + i * 2.7) * 10.0 + sin(t * 1.7 + i * 2.0) * 2.5)

func _process(delta: float) -> void:
	# Nothing to move or draw while Circe is on Aiaia, far out of sight.
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if player and player.global_position.y < COVE_TOP:
		return
	_time += delta
	for i in 6:
		var target := _targets[i]
		if not _pinned[i]:
			target += _drift(i) * _sway
		_heads[i] = _heads[i].lerp(target, 1.0 - exp(-_follow[i] * delta))
		if not _calm and not _striking and _time > _next_snap[i]:
			_open_until[i] = _time + _rng.randf_range(0.2, 0.4)
			_next_snap[i] = _time + _rng.randf_range(2.0, 6.0)
	for i in 6:
		_chains[i] = _neck_chain(i)
	queue_redraw()

func _head_sprite(i: int) -> String:
	var sprite_name: String = POSES[_pose][i][2]
	if _calm and sprite_name.begins_with("front"):
		return "front_calm"
	if _time < _open_until[i]:
		return sprite_name.replace("closed", "open")
	return sprite_name

func _head_at(i: int) -> Vector2:
	return _heads[i].round()

## The neck rule, shared with tools/pixelart/scylla_big.py: a cubic curve from the base to the
## head's socket, with a disc every SPACING pixels, thick at the base and thinner at the head.
func _neck_chain(i: int) -> Array:
	var head: Array = Parts.HEADS[_head_sprite(i)]
	var base := _bases[i]
	var socket := _head_at(i) + Vector2(head[0], head[1])
	var neck_dir := Vector2(head[2], head[3])
	if _head_sprite(i).begins_with("front"):
		# A head turned to face Circe hangs from a hook of neck that comes over from her body's side.
		neck_dir = Vector2(signf(base.x - socket.x) * 0.55, -0.85)
	var d := socket - base
	var length := maxf(d.length(), 1.0)
	var perp := Vector2(-d.y, d.x) / length
	var bulge: float = BULGE[i]
	var lean := base.x / 70.0
	var p1 := base + Vector2(lean * length * 0.25, -length * 0.45) + perp * bulge
	var p2 := socket + neck_dir * length * 0.4 - perp * bulge * 0.5
	var pts := PackedVector2Array()
	for s in 41:
		pts.append(_bezier(base, p1, p2, socket, s / 40.0))
	var cum := PackedFloat32Array([0.0])
	for j in range(1, pts.size()):
		cum.append(cum[j - 1] + pts[j].distance_to(pts[j - 1]))
	var total := cum[cum.size() - 1]
	var out: Array = []
	var s := 0.0
	var j := 0
	while s <= total:
		while j < pts.size() - 2 and cum[j + 1] < s:
			j += 1
		var span := maxf(cum[j + 1] - cum[j], 0.0001)
		var p := pts[j].lerp(pts[j + 1], (s - cum[j]) / span)
		var r := roundi(lerpf(Parts.R_BASE, Parts.R_HEAD, s / total))
		out.append(Vector3i(roundi(p.x), roundi(p.y), r))
		s += Parts.SPACING
	return out

static func _bezier(p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, t: float) -> Vector2:
	var u := 1.0 - t
	return p0 * (u * u * u) + p1 * (3.0 * u * u * t) + p2 * (3.0 * u * t * t) + p3 * (t * t * t)

# ---------------------------------------------------------------------------
# Drawing: the dark of her under the water, her back, the necks (outline pass, then the shaded
# discs, then the pale belly), the heads, and the foam round her. A striking neck is drawn last,
# over the foam.

func _draw() -> void:
	if _texture == null:
		return
	_draw_part(_parts["shadow"], Vector2.ZERO)
	_draw_part(_parts["body"], Vector2.ZERO)
	for i in DRAW_ORDER:
		if not (_striking and i == STRIKER):
			_draw_neck(i)
	_draw_part(_parts["foam%d" % (int(_time * 6.0) % 4)], Vector2.ZERO)
	if _striking:
		_draw_neck(STRIKER)
	if _vial_visible:
		_draw_part(_parts["vial"], _vial_pos)

func _draw_neck(i: int) -> void:
	var chain: Array = _chains[i]
	var outline: Array = _seg["o"]
	var fill: Array = _seg["f"]
	var scaled: Array = _seg["s"]
	var belly: Array = _seg["b"]
	for c in chain:
		_draw_part(outline[c.z], Vector2(c.x, c.y))
	for k in chain.size():
		var c: Vector3i = chain[k]
		_draw_part(scaled[c.z] if k % 3 == 0 else fill[c.z], Vector2(c.x, c.y))
	for k in int(chain.size() * 0.85):
		var c: Vector3i = chain[k]
		_draw_part(belly[c.z], Vector2(c.x, c.y + 1))
	_draw_part(_parts[_head_sprite(i)], _head_at(i))

func _draw_part(part: Array, at: Vector2) -> void:
	var source: Rect2 = part[0]
	draw_texture_rect_region(_texture, Rect2(at - part[1], source.size), source)

# ---------------------------------------------------------------------------
# Cues from the dialogue

func _on_line_cue(dialogue_id: String, cue: String) -> void:
	if not dialogue_id.begins_with("scylla_"):
		return
	print("[Scylla] cue %s" % cue)   # the automated playtest waits on these
	_sequence += 1
	match cue:
		"howl":
			_howl(_sequence)
		"roar":
			var strait := get_tree().get_first_node_in_group("strait")
			if strait:
				strait.roar()
		"descend":
			_set_pose("circe")
		"snap":
			_snap_vial(_sequence)
		"calm":
			_go_calm()
		"wake":
			_wake()
		"strike":
			_strike(_sequence)
		"away":
			_end_strike()
			_set_pose("sea")

func _set_pose(pose: String) -> void:
	_pose = pose
	_calm = false
	_sway = SWAY[pose]
	for i in 6:
		_targets[i] = _pose_target(i)
		_follow[i] = FOLLOW

func _wait(seconds: float) -> Signal:
	return get_tree().create_timer(seconds).timeout

## From up in the mist: all six heads lift and open together.
func _howl(sequence: int) -> void:
	for i in 6:
		_open_until[i] = _time + 1.6
		_targets[i] = _pose_target(i) + Vector2(0, -18)
	await _wait(1.6)
	if sequence == _sequence:
		_set_pose(_pose)

## Circe throws the vial up in an arc; the catching head darts down to meet it and swallows.
func _snap_vial(sequence: int) -> void:
	var player := get_tree().get_first_node_in_group("player") as Node2D
	var start := Vector2(0, 60)
	if player:
		start = (player.global_position - global_position + Vector2(6, -22)).round()
	_vial_visible = true
	var fly := func(t: float) -> void:
		var mouth := _head_at(CATCHER) + Vector2(0, 8)
		_vial_pos = (start.lerp(mouth, t) + Vector2(0, -80.0 * 4.0 * t * (1.0 - t))).round()
	var flight := create_tween()
	flight.tween_method(fly, 0.0, 1.0, 0.65)
	await _wait(0.45)
	if sequence != _sequence:
		_vial_visible = false
		return
	_open_until[CATCHER] = _time + 0.25
	_targets[CATCHER] = _pose_target(CATCHER) + Vector2(4, 26)
	_follow[CATCHER] = 12.0
	await flight.finished
	_vial_visible = false
	SceneManager.shake_camera(0.15, 2.0)
	await _wait(0.2)
	if sequence == _sequence:
		_targets[CATCHER] = _pose_target(CATCHER)
		_follow[CATCHER] = FOLLOW

## For one breath the draught holds: the heads stop where they are, jaws shut, eyes dull.
func _go_calm() -> void:
	_calm = true
	_sway = 0.0
	for i in 6:
		_open_until[i] = 0.0
		_targets[i] = _heads[i]
		_follow[i] = 4.0

## Then she breathes out: the heads rear a little and snarl, restless again.
func _wake() -> void:
	_calm = false
	_sway = 0.8
	for i in 6:
		_targets[i] = _pose_target(i) + Vector2(0, -14)
		_follow[i] = 5.0
		_open_until[i] = _time + 0.3 + i * 0.07

## She screams with every mouth; one head rears back and drives down onto the rock beside Circe.
func _strike(sequence: int) -> void:
	_set_pose("circe")
	_sway = 1.0
	_striking = true
	for i in 6:
		_open_until[i] = _time + 1.8
	_targets[STRIKER] = Vector2(_bases[STRIKER].x - 12.0, -330.0)
	_follow[STRIKER] = REAR
	await _wait(0.4)
	if sequence != _sequence:
		return
	var hit := (STRIKE_AT - global_position).round()
	_pinned[STRIKER] = true
	_targets[STRIKER] = hit
	_follow[STRIKER] = LUNGE
	await _wait(0.13)
	if sequence != _sequence:
		return
	_heads[STRIKER] = hit
	_impact(hit)
	await _wait(0.5)
	if sequence != _sequence:
		return
	_open_until[STRIKER] = 0.0
	await _wait(0.35)
	if sequence == _sequence:
		_end_strike()

func _end_strike() -> void:
	if not _striking:
		return
	_striking = false
	_pinned[STRIKER] = false
	_targets[STRIKER] = _pose_target(STRIKER)
	_follow[STRIKER] = 3.0

## Stone chips and spray where the head hits, a thud, and the screen jolts.
func _impact(at: Vector2) -> void:
	SceneManager.shake_camera(0.5, 10.0)
	AudioController.play_sfx("plant")
	_burst(at + Vector2(0, 8), Color(0.42, 0.38, 0.36), 18, Vector2(70, 160), 1.0)
	_burst(at + Vector2(0, 10), Color(0.85, 0.93, 0.96), 14, Vector2(40, 110), 1.5)

func _burst(at: Vector2, colour: Color, amount: int, speed: Vector2, size: float) -> void:
	var chips := CPUParticles2D.new()
	chips.texture = _pixel_texture()
	chips.position = at
	chips.one_shot = true
	chips.explosiveness = 1.0
	chips.amount = amount
	chips.lifetime = 0.8
	chips.direction = Vector2(0, -1)
	chips.spread = 75.0
	chips.gravity = Vector2(0, 340)
	chips.initial_velocity_min = speed.x
	chips.initial_velocity_max = speed.y
	chips.scale_amount_min = size
	chips.scale_amount_max = size + 0.5
	chips.color = colour
	add_child(chips)
	chips.emitting = true
	get_tree().create_timer(1.5).timeout.connect(chips.queue_free)

static func _pixel_texture() -> ImageTexture:
	var image := Image.create(2, 2, false, Image.FORMAT_RGBA8)
	image.fill(Color.WHITE)
	return ImageTexture.create_from_image(image)
