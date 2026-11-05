extends Node2D
## A small butterfly drawn in code: two wing pairs that flap, a dark body, and a lazy looping
## flight around the point where it was placed. Purely decorative; nothing collides with it.

@export var wing_color: Color = Color(0.98, 0.93, 0.62)
@export var radius: Vector2 = Vector2(46, 26)

var _anchor: Vector2
var _time: float = 0.0
var _speed: float = 1.0
var _phase: float = 0.0
var _flap_rate: float = 15.0

func _ready() -> void:
	_anchor = position
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(name) + int(position.x * 31.0 + position.y)
	_speed = rng.randf_range(0.5, 0.9)
	_phase = rng.randf_range(0.0, TAU)
	_flap_rate = rng.randf_range(12.0, 17.0)
	_time = rng.randf_range(0.0, 20.0)
	z_index = 7
	scale = Vector2(1.5, 1.5)

func _process(delta: float) -> void:
	_time += delta
	var t := _time * _speed
	# Two loops at different rates give a wandering figure-of-eight; a small bob rides on top.
	position = _anchor + Vector2(sin(t + _phase) * radius.x, sin(t * 1.7 + _phase * 0.5) * radius.y)
	position.y += sin(_time * 6.0) * 2.0
	queue_redraw()

func _draw() -> void:
	var flap := absf(sin(_time * _flap_rate))      # 0 = wings closed, 1 = wings open
	var span := 1.0 + flap * 3.0
	var heading := signf(cos(_time * _speed + _phase))
	var shade := wing_color.darkened(0.25)
	# Upper and lower wing on each side, mirrored.
	for side in [-1.0, 1.0]:
		var s: float = side * heading
		draw_colored_polygon(PackedVector2Array([Vector2(0, -1), Vector2(s * span, -4), Vector2(s * span * 0.9, 0)]), wing_color)
		draw_colored_polygon(PackedVector2Array([Vector2(0, 0), Vector2(s * span * 0.8, 1), Vector2(s * span * 0.5, 3)]), shade)
	draw_line(Vector2(0, -2), Vector2(0, 2), Color(0.18, 0.12, 0.08), 1.0)
