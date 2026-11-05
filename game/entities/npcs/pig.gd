extends Node2D
## A pig that roams near where it was placed, picking walk, run, eat, sleep or idle at random.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const SpriteSheet := preload("res://game/util/sprite_sheet.gd")
const PIG_IDLE_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_idle.png"
const PIG_WALK_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_walk.png"
const PIG_RUN_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_run.png"
const PIG_EAT_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_eat.png"
const PIG_SLEEP_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_sleep.png"

@export var roam_radius: float = 80.0
@export var walk_speed: float = 22.0
@export var run_speed: float = 44.0
@export var idle_duration: Vector2 = Vector2(1.0, 2.6)
@export var eat_duration: Vector2 = Vector2(1.2, 2.4)
@export var sleep_duration: Vector2 = Vector2(2.5, 4.2)
@export var walk_duration: Vector2 = Vector2(1.0, 2.2)
@export var run_duration: Vector2 = Vector2(0.6, 1.4)

@onready var sprite: AnimatedSprite2D = $Sprite

var _origin: Vector2
var _target: Vector2
var _state: String = "idle"
var _state_timer: float = 0.0
var _facing: String = "right"
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	z_index = 3
	_origin = global_position
	_rng.seed = int(global_position.x * 991.0 + global_position.y * 977.0)
	_setup_animations()
	_enter_state("idle")

func _process(delta: float) -> void:
	_state_timer -= delta

	if _state == "walk" or _state == "run":
		var speed := walk_speed if _state == "walk" else run_speed
		var to_target := _target - global_position
		if to_target.length() < 2.0:
			global_position = _target
			_state_timer = 0.0
		else:
			var movement := to_target.normalized() * speed * delta
			global_position += movement
			_set_movement_facing(to_target)

	if _state_timer <= 0.0:
		_choose_next_state()

func _setup_animations() -> void:
	# Walk and run sheets have four facings; idle, eat and sleep only face left or right.
	var frames := SpriteFrames.new()
	var four := SpriteSheet.FOUR_WAY_ROWS
	var side := SpriteSheet.SIDE_ROWS
	SpriteSheet.add_animations(frames, "walk", TextureLoaderUtil.load_texture(PIG_WALK_PATH), four, 6.0)
	SpriteSheet.add_animations(frames, "run", TextureLoaderUtil.load_texture(PIG_RUN_PATH), four, 8.0)
	SpriteSheet.add_animations(frames, "idle", TextureLoaderUtil.load_texture(PIG_IDLE_PATH), side, 4.5)
	SpriteSheet.add_animations(frames, "eat", TextureLoaderUtil.load_texture(PIG_EAT_PATH), side, 4.5)
	SpriteSheet.add_animations(frames, "sleep", TextureLoaderUtil.load_texture(PIG_SLEEP_PATH), side, 4.5)
	sprite.sprite_frames = frames

func _choose_next_state() -> void:
	var roll := _rng.randi_range(0, 99)
	if roll < 15:
		_enter_state("run")
	elif roll < 45:
		_enter_state("walk")
	elif roll < 65:
		_enter_state("eat")
	elif roll < 80:
		_enter_state("sleep")
	else:
		_enter_state("idle")

func _enter_state(next_state: String) -> void:
	_state = next_state
	match _state:
		"run":
			_target = _random_target()
			_state_timer = _rng.randf_range(run_duration.x, run_duration.y)
			_play_if_exists("run_%s" % SpriteSheet.facing_from(_target - global_position))
		"walk":
			_target = _random_target()
			_state_timer = _rng.randf_range(walk_duration.x, walk_duration.y)
			_play_if_exists("walk_%s" % SpriteSheet.facing_from(_target - global_position))
		"eat":
			_state_timer = _rng.randf_range(eat_duration.x, eat_duration.y)
			_play_if_exists("eat_%s" % _lateral_facing())
		"sleep":
			_state_timer = _rng.randf_range(sleep_duration.x, sleep_duration.y)
			_play_if_exists("sleep_%s" % _lateral_facing())
		_:
			_state_timer = _rng.randf_range(idle_duration.x, idle_duration.y)
			_play_if_exists("idle_%s" % _lateral_facing())

func _random_target() -> Vector2:
	return _origin + Vector2(
		_rng.randf_range(-roam_radius, roam_radius),
		_rng.randf_range(-roam_radius * 0.5, roam_radius * 0.5)
	)

func _set_movement_facing(direction: Vector2) -> void:
	_facing = SpriteSheet.facing_from(direction)
	var animation_name := "%s_%s" % [_state, _facing]
	if sprite.sprite_frames and sprite.sprite_frames.has_animation(animation_name) and sprite.animation != animation_name:
		sprite.play(animation_name)

func _lateral_facing() -> String:
	return "right" if _facing == "right" else "left"

func _play_if_exists(animation_name: String) -> void:
	if sprite.sprite_frames and sprite.sprite_frames.has_animation(animation_name):
		sprite.play(animation_name)
