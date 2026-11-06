extends Node2D
## A seagull drawn in code: a few pixels of white body and grey-tipped wings that flap, then
## glide, as it circles slowly over the sea round Aiaia. Purely for life on the screen.

@export var centre := Vector2(270, 1250)
@export var radius := Vector2(170, 50)
## Radians per second round the circle; negative flies the other way.
@export var speed := 0.22
@export var phase := 0.0

const WHITE := Color(0.96, 0.96, 0.93)
const GREY := Color(0.62, 0.65, 0.68)
const TIP := Color(0.18, 0.18, 0.2)
const SHADE := Color(0.82, 0.83, 0.84)

var _t := 0.0
var _flap := 0.0
var _gliding := false
var _switch_at := 1.5

func _ready() -> void:
	z_index = 30
	_t = phase
	_switch_at = randf_range(1.0, 2.5)

func _process(delta: float) -> void:
	_t += delta
	var angle := _t * speed + phase
	var pos := centre + Vector2(cos(angle) * radius.x, sin(angle) * radius.y)
	position = pos.round()
	# Flap in bursts, glide in between.
	_switch_at -= delta
	if _switch_at <= 0.0:
		_gliding = not _gliding
		_switch_at = randf_range(1.2, 2.8) if _gliding else randf_range(0.8, 1.6)
	if not _gliding:
		_flap += delta * 7.0
	queue_redraw()

func _px(x: int, y: int, c: Color) -> void:
	draw_rect(Rect2(x, y, 1, 1), c)

func _draw() -> void:
	# Heading: left or right along the circle.
	var going_left := cos(_t * speed + phase + PI / 2.0) * signf(speed) < 0.0
	var s := -1 if going_left else 1
	var up := (not _gliding) and fmod(_flap, 2.0) < 1.0
	# Body and head.
	_px(0, 0, WHITE); _px(1 * s, 0, WHITE); _px(-1 * s, 0, SHADE)
	_px(2 * s, -1, WHITE)
	_px(3 * s, -1, Color(0.95, 0.75, 0.25))   # beak
	if up:
		# Wings raised in a V.
		for i in range(1, 4):
			_px(-i, -i, GREY if i < 3 else TIP)
			_px(i, -i, GREY if i < 3 else TIP)
	else:
		# Wings spread flat, a gentle droop at the tips.
		for i in range(1, 5):
			var dy := 0 if i < 4 else 1
			_px(-i, dy, GREY if i < 4 else TIP)
			_px(i, dy, GREY if i < 4 else TIP)
