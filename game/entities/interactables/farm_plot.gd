extends Area2D
## One of the three garden plots: plants a moly seed, shows its growth, harvests it.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const STAGE_TEXTURES := {
	"empty": "res://assets/image_pipeline/generated/raw/sprites/entities/farm_plot_stage_empty.png",
	"planted": "res://assets/image_pipeline/generated/raw/sprites/entities/farm_plot_stage_planted.png",
	"stage_1": "res://assets/image_pipeline/generated/raw/sprites/entities/farm_plot_stage_1.png",
	"stage_2": "res://assets/image_pipeline/generated/raw/sprites/entities/farm_plot_stage_2.png",
	"ready": "res://assets/image_pipeline/generated/raw/sprites/entities/farm_plot_stage_ready.png",
}

@export var plot_id: Vector2i = Vector2i(0, 0)

@onready var sprite: Sprite2D = $Sprite
@onready var label: Label = $Label

var _textures: Dictionary = {}

func _ready() -> void:
	for key in STAGE_TEXTURES:
		_textures[key] = TextureLoaderUtil.load_texture(STAGE_TEXTURES[key])
	GameState.crop_planted.connect(_on_plot_changed)
	GameState.crop_harvested.connect(_on_plot_changed)
	GameState.day_advanced.connect(_on_day_advanced)
	_update_display()

func interact() -> void:
	var plot_data = GameState.farm_plots.get(plot_id)
	if plot_data == null:
		if GameState.plant_seed(plot_id):
			AudioController.play_sfx("plant")
			DialogueBox.open(self, "farm_planting")
		else:
			DialogueBox.open(self, "farm_no_seeds")
	elif plot_data.get("ready", false):
		GameState.harvest_crop(plot_id)
		AudioController.play_sfx("harvest")
		DialogueBox.open(self, "farm_harvest")
	else:
		DialogueBox.open(self, "farm_growing")

func _on_plot_changed(_position: Vector2i, _crop_id: String) -> void:
	_update_display()

func _on_day_advanced(_new_day: int) -> void:
	_update_display()

func _update_display() -> void:
	var plot_data = GameState.farm_plots.get(plot_id)
	if plot_data == null:
		_show_stage("empty", "Empty")
	elif plot_data.get("ready", false):
		_show_stage("ready", "Ready!")
	elif plot_data.get("stage", 0) == 0:
		_show_stage("planted", "Planted")
	elif plot_data.get("stage", 0) == 1:
		_show_stage("stage_1", "Growing...")
	else:
		_show_stage("stage_2", "Growing...")

func _show_stage(key: String, text: String) -> void:
	var texture: Texture2D = _textures.get(key)
	sprite.texture = texture if texture else _textures.get("empty")
	label.text = text
