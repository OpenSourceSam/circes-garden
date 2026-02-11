extends Area2D

@export var plot_id: Vector2i = Vector2i(0, 0)

@onready var sprite: Sprite2D = $Sprite
@onready var label: Label = $Label

func _ready() -> void:
	add_to_group("farm_plots")
	# Connect to GameState signals for reactive updates
	GameState.crop_planted.connect(_on_state_changed)
	GameState.crop_harvested.connect(_on_state_changed)
	_update_display()

func interact() -> void:
	var plot_data = GameState.farm_plots.get(plot_id)
	if plot_data == null:
		# Empty plot - try to plant
		if GameState.has_item("moly_seed"):
			GameState.remove_item("moly_seed", 1)
			GameState.plant_crop(plot_id, "moly")
			AudioController.play_sfx("plant")
			_show_dialogue("planting", [
				{"speaker": "", "text": "*You press the golden seed into the dark soil.*"},
				{"speaker": "Circe", "text": "Grow well, little one."},
			])
		else:
			_show_dialogue("no_seeds", [
				{"speaker": "Circe", "text": "I need moly seeds to plant here."},
			])
	elif plot_data.get("ready", false):
		# Ready to harvest
		GameState.harvest_crop(plot_id)
		AudioController.play_sfx("harvest")
		_show_dialogue("harvest", [
			{"speaker": "", "text": "*The golden moly comes free with a gentle tug.*"},
			{"speaker": "Circe", "text": "Beautiful. This is the herb that heals."},
		])
	else:
		# Still growing
		_show_dialogue("growing", [
			{"speaker": "Circe", "text": "Not yet. It needs more time."},
		])

func _show_dialogue(id: String, lines: Array) -> void:
	var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
	if dialogue_box and not dialogue_box.is_active():
		var d = DialogueData.new()
		d.id = "farm_%s" % id
		d.lines = lines
		dialogue_box.start_dialogue(d)

func _on_state_changed(_position: Vector2i, _crop_id: String) -> void:
	_update_display()

func _update_display() -> void:
	var plot_data = GameState.farm_plots.get(plot_id)

	if plot_data == null:
		# Empty plot
		sprite.modulate = Color(0.4, 0.3, 0.2)
		label.text = "Empty"
	else:
		var stage: int = plot_data.get("stage", 0)
		var is_ready: bool = plot_data.get("ready", false)

		if is_ready:
			# Stage 3/ready: bright yellow-green
			sprite.modulate = Color(0.9, 0.9, 0.3)
			label.text = "Ready!"
		elif stage == 0:
			# Just planted: dark green
			sprite.modulate = Color(0.3, 0.4, 0.2)
			label.text = "Planted"
		elif stage == 1:
			# Growing stage 1: medium green
			sprite.modulate = Color(0.4, 0.6, 0.3)
			label.text = "Growing..."
		elif stage == 2:
			# Growing stage 2: light green
			sprite.modulate = Color(0.6, 0.7, 0.3)
			label.text = "Growing..."
		else:
			# Fallback: treat as mature
			sprite.modulate = Color(0.9, 0.9, 0.3)
			label.text = "Ready!"
