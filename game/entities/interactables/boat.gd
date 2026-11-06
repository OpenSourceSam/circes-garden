extends Area2D
## A boat between Aiaia and the cove. Sails to `destination`, once `requires_flag` is set.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const BOAT_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/boat.png"

@export var destination: Vector2 = Vector2.ZERO
@export var requires_flag: String = ""
## Shifts the picture only (not the place Circe walks to), e.g. to keep the sail off a pier.
@export var sprite_offset: Vector2 = Vector2.ZERO

@onready var sprite: Sprite2D = $Sprite

## The boat rides the swell: one pixel up and down, slowly (whole pixels, so the art stays crisp).
const BOB_SPEED := 1.6
var _rest_position := Vector2.ZERO
var _time := 0.0

func _ready() -> void:
	sprite.texture = TextureLoaderUtil.load_texture(BOAT_TEXTURE_PATH)
	sprite.position += sprite_offset
	_rest_position = sprite.position
	_time = fmod(global_position.x * 0.37 + global_position.y * 0.11, TAU)

func _process(delta: float) -> void:
	_time += delta * BOB_SPEED
	sprite.position = _rest_position + Vector2(0, roundf(sin(_time)))

func prompt_text() -> String:
	return "Take the boat"

func interact() -> void:
	if requires_flag != "" and not GameState.get_flag(requires_flag):
		DialogueBox.open(self, "boat_blocked")
		return
	AudioController.play_sfx("ui_confirm")
	SceneManager.teleport_player(destination)
