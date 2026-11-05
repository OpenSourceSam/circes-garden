extends CharacterBody2D
## Circe. Walks with the arrow keys, WASD or a d-pad and interacts with whatever is in reach.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const SpriteSheet := preload("res://game/util/sprite_sheet.gd")
const WorldLabel := preload("res://game/util/world_label.gd")
const CIRCE_IDLE_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/circe/circe_idle.png"
const CIRCE_WALK_PATH := "res://assets/image_pipeline/generated/raw/sprites/characters/circe/circe_walk.png"
const DUST_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/ui/particle_soft.png"
## The playable strip is 540 px wide and the map 3500 px tall; keep a margin for the sprite.
const WALK_BOUNDS := Rect2(16.0, 24.0, 508.0, 3456.0)
const POSITION_REPORT_INTERVAL := 0.1

@export var speed: float = 100.0

@onready var interaction_label: Label = $InteractionPrompt
@onready var sprite: AnimatedSprite2D = $Sprite

var _nearby_interactable: Node = null
var _facing: String = "down"
var _position_report_timer: float = 0.0
var _was_moving: bool = false
var _dust: CPUParticles2D

func _ready() -> void:
	add_to_group("player")
	WorldLabel.setup(interaction_label, -30.0)
	interaction_label.hide()
	_setup_animations()
	_setup_dust()

func _setup_dust() -> void:
	_dust = CPUParticles2D.new()
	_dust.name = "Dust"
	_dust.texture = TextureLoaderUtil.load_texture(DUST_TEXTURE_PATH)
	_dust.amount = 10
	_dust.lifetime = 0.45
	_dust.emitting = false
	_dust.position = Vector2(0, 14)
	_dust.direction = Vector2(0, -1)
	_dust.spread = 70.0
	_dust.gravity = Vector2(0, 0)
	_dust.initial_velocity_min = 8.0
	_dust.initial_velocity_max = 22.0
	_dust.scale_amount_min = 0.25
	_dust.scale_amount_max = 0.45
	_dust.color = Color(0.78, 0.68, 0.48, 0.55)
	_dust.z_index = -1
	add_child(_dust)

func _physics_process(delta: float) -> void:
	var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = input_dir * speed
	move_and_slide()
	global_position = global_position.clamp(WALK_BOUNDS.position, WALK_BOUNDS.end)
	var moving := input_dir.length() > 0.01
	_update_animation(input_dir, moving)
	_dust.emitting = moving
	_report_position(delta, moving)

func _report_position(delta: float, moving: bool) -> void:
	# Console breadcrumbs for the automated playtest (tools/pixelart/playtest.py).
	_position_report_timer += delta
	if (moving and _position_report_timer >= POSITION_REPORT_INTERVAL) or (_was_moving and not moving):
		_position_report_timer = 0.0
		print("[Player] at %d,%d" % [int(global_position.x), int(global_position.y)])
	_was_moving = moving

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") and _nearby_interactable:
		# Consume the press so the dialogue it may open does not also read it as "continue".
		get_viewport().set_input_as_handled()
		_nearby_interactable.interact()
		call_deferred("refresh_prompt")

## Dialogue and the herb lesson pause Circe; the prompt hides with her controls.
func set_controls_enabled(enabled: bool) -> void:
	set_physics_process(enabled)
	set_process_unhandled_input(enabled)
	interaction_label.visible = enabled and _nearby_interactable != null and is_instance_valid(_nearby_interactable)
	if enabled:
		refresh_prompt()

func _on_interaction_zone_body_entered(body: Node) -> void:
	if body != self and body.has_method("interact"):
		_set_target(body)

func _on_interaction_zone_body_exited(body: Node) -> void:
	if body == _nearby_interactable:
		_set_target(null)

func _on_interaction_zone_area_entered(area: Area2D) -> void:
	if area.has_method("interact"):
		_set_target(area)

func _on_interaction_zone_area_exited(area: Area2D) -> void:
	if area == _nearby_interactable:
		_set_target(null)

## One prompt at a time: while Circe is in reach of something, its own floating label is hidden
## and the prompt above her head says what E will do ("E  Talk to Hermes").
func _set_target(target: Node) -> void:
	if _nearby_interactable and is_instance_valid(_nearby_interactable) and _nearby_interactable.has_method("world_label"):
		var old_label: Label = _nearby_interactable.world_label()
		if old_label:
			old_label.show()
	_nearby_interactable = target
	if target == null:
		interaction_label.hide()
		return
	refresh_prompt()
	if target.has_method("world_label"):
		var label: Label = target.world_label()
		if label:
			label.hide()
	interaction_label.show()

## Re-reads the prompt from the target, e.g. after a plot was planted or harvested.
func refresh_prompt() -> void:
	if _nearby_interactable == null or not is_instance_valid(_nearby_interactable):
		return
	var action := "Interact"
	if _nearby_interactable.has_method("prompt_text"):
		action = _nearby_interactable.prompt_text()
	interaction_label.text = "E  %s" % action

func _setup_animations() -> void:
	var frames := SpriteFrames.new()
	SpriteSheet.add_animations(frames, "idle", TextureLoaderUtil.load_texture(CIRCE_IDLE_PATH), SpriteSheet.FOUR_WAY_ROWS, 4.0)
	SpriteSheet.add_animations(frames, "walk", TextureLoaderUtil.load_texture(CIRCE_WALK_PATH), SpriteSheet.FOUR_WAY_ROWS, 6.0)
	sprite.sprite_frames = frames
	_update_animation(Vector2.ZERO, false)

func _update_animation(input_dir: Vector2, moving: bool) -> void:
	if moving:
		_facing = SpriteSheet.facing_from(input_dir)
	var animation_name := "%s_%s" % ["walk" if moving else "idle", _facing]
	if sprite.sprite_frames.has_animation(animation_name) and sprite.animation != animation_name:
		sprite.play(animation_name)
