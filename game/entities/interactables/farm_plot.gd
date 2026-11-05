extends Area2D
## One of the three garden plots: plants a moly seed, shows its growth, harvests it.

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const SPARKLE_TEXTURE := "res://assets/image_pipeline/generated/raw/sprites/ui/particle_soft.png"
const WorldLabel := preload("res://game/util/world_label.gd")
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
	WorldLabel.setup(label, -18.0)
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
			_sparkle(Color(0.75, 0.6, 0.4), 10)
			DialogueBox.open(self, "farm_planting")
		else:
			DialogueBox.open(self, "farm_no_seeds")
	elif plot_data.get("ready", false):
		GameState.harvest_crop(plot_id)
		AudioController.play_sfx("harvest")
		_sparkle(Color(1.0, 0.95, 0.7), 22)
		DialogueBox.open(self, "farm_harvest")
	else:
		DialogueBox.open(self, "farm_growing")

func prompt_text() -> String:
	var plot_data = GameState.farm_plots.get(plot_id)
	if plot_data == null:
		return "Plant a moly seed" if GameState.get_item_count("moly_seed") > 0 else "An empty plot"
	if plot_data.get("ready", false):
		return "Harvest the moly"
	return "Check the moly"

func world_label() -> Label:
	return label

## A small one-shot burst: soil when planting, motes of light when the moly comes up.
func _sparkle(color: Color, amount: int) -> void:
	var burst := CPUParticles2D.new()
	burst.texture = TextureLoaderUtil.load_texture(SPARKLE_TEXTURE)
	burst.one_shot = true
	burst.explosiveness = 0.9
	burst.amount = amount
	burst.lifetime = 0.9
	burst.direction = Vector2(0, -1)
	burst.spread = 70.0
	burst.gravity = Vector2(0, 60)
	burst.initial_velocity_min = 30.0
	burst.initial_velocity_max = 70.0
	burst.scale_amount_min = 0.12
	burst.scale_amount_max = 0.3
	burst.color = color
	burst.z_index = 8
	add_child(burst)
	burst.emitting = true
	get_tree().create_timer(1.5).timeout.connect(burst.queue_free)

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
