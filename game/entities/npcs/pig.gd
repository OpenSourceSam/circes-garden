extends Node2D
## A pig that roams near where it was placed, picking walk, run, eat, sleep or idle at random.
## When Circe walks near, a pig that is awake stops and turns to look at her.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const SpriteSheet := preload("res://game/util/sprite_sheet.gd")
const PIG_IDLE_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_idle.png"
const PIG_WALK_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_walk.png"
const PIG_RUN_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_run.png"
const PIG_EAT_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_eat.png"
const PIG_SLEEP_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/pig/pig_sleep.png"

@export var roam_radius: float = 80.0
## How the pig is first seen (pigs side by side should not look like one picture pasted twice).
@export var start_state: String = ""
@export var start_facing: String = ""
@export var walk_speed: float = 22.0
@export var run_speed: float = 44.0
@export var idle_duration: Vector2 = Vector2(1.0, 2.6)
@export var eat_duration: Vector2 = Vector2(1.2, 2.4)
@export var sleep_duration: Vector2 = Vector2(2.5, 4.2)
@export var walk_duration: Vector2 = Vector2(1.0, 2.2)
@export var run_duration: Vector2 = Vector2(0.6, 1.4)

@onready var sprite: AnimatedSprite2D = $Sprite

## How close Circe has to come before an awake pig stops to watch her (the pen is about four
## tiles from the path, so pigs look up as she walks by).
const NOTICE_DISTANCE := 140.0
var _player: Node2D = null

var _origin: Vector2
var _target: Vector2
var _state: String = "idle"
var _state_timer: float = 0.0
var _facing: String = "right"
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	# Sorted with the fences by y (world.gd), so the pen's front rail passes in front of a pig.
	z_index = 0
	_origin = global_position
	_rng.seed = int(global_position.x * 991.0 + global_position.y * 977.0)
	_setup_animations()
	preload("res://game/util/ground_shadow.gd").attach(self, Vector2(0, 14), Vector2(17, 5))
	var cell := int(global_position.x) / 8 + int(global_position.y) / 8
	_facing = start_facing if start_facing != "" else ("right" if cell % 2 == 1 else "left")
	_enter_state(start_state if start_state != "" else "idle")
	sprite.frame = cell % 4

func _process(delta: float) -> void:
	_state_timer -= delta
	_watch_circe()

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

func _watch_circe() -> void:
	if _state == "sleep":
		return
	if _player == null or not is_instance_valid(_player):
		_player = get_tree().get_first_node_in_group("player") as Node2D
		if _player == null:
			return
	var offset := _player.global_position - global_position
	if offset.length() > NOTICE_DISTANCE or absf(offset.x) < 4.0:
		return
	var face := "right" if offset.x > 0.0 else "left"
	if _state != "idle" or face != _facing:
		_facing = face
		_state = "idle"
		_state_timer = _rng.randf_range(1.2, 2.2)
		_play_if_exists("idle_%s" % face)

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
