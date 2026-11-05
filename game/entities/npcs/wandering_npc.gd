extends CharacterBody2D
## An NPC that stands idle, then takes a short walk to a random point near where it was
## placed, and repeats. Hermes and Scylla extend this; their scenes set the sheets and timings.

const SpriteSheet := preload("res://game/util/sprite_sheet.gd")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")

@export_file("*.png") var idle_sheet: String = ""
@export_file("*.png") var walk_sheet: String = ""
@export var idle_fps: float = 3.0
@export var walk_fps: float = 5.0
@export var start_facing: String = "down"
@export var wander_radius: float = 28.0
@export var wander_speed: float = 36.0
@export var walk_duration: Vector2 = Vector2(1.0, 2.2)
@export var idle_duration: Vector2 = Vector2(1.2, 2.6)

@onready var sprite: AnimatedSprite2D = $Sprite

var _origin: Vector2
var _move_target: Vector2
var _state_timer: float = 0.0
var _walking: bool = false
var _facing: String
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	_origin = global_position
	_rng.seed = int(global_position.x * 1000.0 + global_position.y)
	_facing = start_facing
	var frames := SpriteFrames.new()
	SpriteSheet.add_animations(frames, "idle", TextureLoaderUtil.load_texture(idle_sheet), SpriteSheet.FOUR_WAY_ROWS, idle_fps)
	SpriteSheet.add_animations(frames, "walk", TextureLoaderUtil.load_texture(walk_sheet), SpriteSheet.FOUR_WAY_ROWS, walk_fps)
	sprite.sprite_frames = frames
	_switch_to_idle()

func _physics_process(delta: float) -> void:
	_state_timer -= delta
	if _state_timer <= 0.0:
		if _walking:
			_switch_to_idle()
		else:
			_start_walk()

	if not _walking:
		velocity = Vector2.ZERO
		return
	var to_target := _move_target - global_position
	if to_target.length() < 2.0:
		global_position = _move_target
		_switch_to_idle()
		return
	velocity = to_target.normalized() * wander_speed
	move_and_slide()
	_play("walk_" + SpriteSheet.facing_from(velocity))

func _start_walk() -> void:
	_walking = true
	_move_target = _origin + Vector2(
		_rng.randf_range(-wander_radius, wander_radius),
		_rng.randf_range(-wander_radius, wander_radius)
	)
	_state_timer = _rng.randf_range(walk_duration.x, walk_duration.y)

func _switch_to_idle() -> void:
	_walking = false
	velocity = Vector2.ZERO
	_state_timer = _rng.randf_range(idle_duration.x, idle_duration.y)
	_play("idle_" + _facing)

func _play(animation_name: String) -> void:
	_facing = animation_name.get_slice("_", 1)
	if sprite.sprite_frames.has_animation(animation_name) and sprite.animation != animation_name:
		sprite.play(animation_name)
