extends Area2D
## A boat between Aiaia and the cove. Sails to `destination`, once `requires_flag` is set.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const BOAT_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/boat.png"

@export var destination: Vector2 = Vector2.ZERO
@export var requires_flag: String = ""

@onready var sprite: Sprite2D = $Sprite

func _ready() -> void:
	sprite.texture = TextureLoaderUtil.load_texture(BOAT_TEXTURE_PATH)

func prompt_text() -> String:
	return "Take the boat"

func interact() -> void:
	if requires_flag != "" and not GameState.get_flag(requires_flag):
		DialogueBox.open(self, "boat_blocked")
		return
	AudioController.play_sfx("ui_confirm")
	SceneManager.teleport_player(destination)
