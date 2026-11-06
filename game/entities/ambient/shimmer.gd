extends Node2D
## Light glinting on the sea round Aiaia: short pale dashes that brighten and fade at their own
## pace, so the painted water (tools/pixelart/coast.py) moves a little.

## Areas of open water (world pixels) to scatter the glints over, and areas to keep clear (the
## pier and the boat).
@export var areas: Array[Rect2] = [Rect2(0, 1060, 544, 440), Rect2(0, 0, 16, 1040), Rect2(528, 0, 16, 1040),
		Rect2(0, 0, 544, 14)]
@export var keep_clear: Array[Rect2] = [Rect2(205, 980, 200, 200)]
@export var count := 46

const COLOR := Color(0.78, 0.92, 0.9)

var _glints: Array = []          # [position, length, period, offset]
var _t := 0.0

func _ready() -> void:
	z_index = -5                  # above the ground tiles, under everything standing on them
	var rng := RandomNumberGenerator.new()
	rng.seed = 4242
	var total_area := 0.0
	for r in areas:
		total_area += r.get_area()
	var tries := 0
	while _glints.size() < count and tries < count * 20:
		tries += 1
		var pick := rng.randf() * total_area
		var rect: Rect2 = areas[0]
		for r in areas:
			if pick <= r.get_area():
				rect = r
				break
			pick -= r.get_area()
		var p := Vector2(rng.randf_range(rect.position.x, rect.end.x), rng.randf_range(rect.position.y, rect.end.y)).floor()
		var blocked := false
		for k in keep_clear:
			if k.has_point(p):
				blocked = true
		if blocked:
			continue
		_glints.append([p, rng.randi_range(2, 4), rng.randf_range(2.2, 4.5), rng.randf() * TAU])

func _process(delta: float) -> void:
	_t += delta
	queue_redraw()

func _draw() -> void:
	for g in _glints:
		var a: float = sin(_t * TAU / g[2] + g[3])
		if a <= 0.35:
			continue
		var c := COLOR
		c.a = (a - 0.35) / 0.65 * 0.85
		var p: Vector2 = g[0]
		draw_rect(Rect2(p.x, p.y, g[1], 1), c)
		if a > 0.85:
			draw_rect(Rect2(p.x + 1, p.y - 1, 1, 1), Color(1, 1, 1, c.a * 0.8))
