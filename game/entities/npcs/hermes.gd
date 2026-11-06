extends "res://game/entities/npcs/wandering_npc.gd"
## Hermes on the terrace. What he says follows the quest; his first talk opens the herb
## lesson and his last one ends the game.

const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const WorldLabel := preload("res://game/util/world_label.gd")
const HERB_MINIGAME := preload("res://game/scenes/herb_minigame.tscn")

func _ready() -> void:
	super()
	WorldLabel.setup($Label, -46.0)
	preload("res://game/util/ground_shadow.gd").attach(self, Vector2(0, 18), Vector2(13, 5))

func prompt_text() -> String:
	return "Talk to Hermes"

func world_label() -> Label:
	return $Label

func interact() -> void:
	var box = DialogueBox.open(self, _current_dialogue_id())
	if box and not box.dialogue_ended.is_connected(_on_dialogue_ended):
		box.dialogue_ended.connect(_on_dialogue_ended)
	if box and not box.line_shown.is_connected(_on_line_shown):
		box.line_shown.connect(_on_line_shown)

func _current_dialogue_id() -> String:
	if not GameState.get_flag("met_hermes"):
		return "hermes_intro"
	if GameState.get_flag("quest_5_active"):
		return "hermes_epilogue"
	if GameState.get_flag("quest_4_active"):
		return "hermes_sailing"
	if GameState.get_flag("quest_3_active"):
		return "hermes_crafting"
	if GameState.get_flag("quest_2_active"):
		return "hermes_farming"
	return "hermes_default"

## In the epilogue Hermes leaves on the line that says so: a flash of gold and he is gone.
func _on_line_shown(dialogue_id: String, text: String) -> void:
	if dialogue_id == "hermes_epilogue" and "flicker" in text and visible:
		_vanish()

func _vanish() -> void:
	set_physics_process(false)
	var burst := CPUParticles2D.new()
	burst.texture = load("res://assets/image_pipeline/generated/raw/sprites/ui/particle_soft.png")
	burst.one_shot = true
	burst.explosiveness = 0.95
	burst.amount = 28
	burst.lifetime = 1.0
	burst.direction = Vector2(0, -1)
	burst.spread = 180.0
	burst.gravity = Vector2(0, -20)
	burst.initial_velocity_min = 40.0
	burst.initial_velocity_max = 110.0
	burst.scale_amount_min = 0.15
	burst.scale_amount_max = 0.4
	burst.color = Color(1.0, 0.85, 0.4)
	burst.global_position = global_position + Vector2(0, -20)
	burst.z_index = 9
	get_parent().add_child(burst)
	burst.emitting = true
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "modulate", Color(2.0, 1.7, 0.6, 0.0), 0.35)
	tween.tween_property(self, "position:y", position.y - 24.0, 0.35).set_ease(Tween.EASE_IN)
	tween.chain().tween_callback(hide)
	AudioController.play_sfx("ui_confirm")

func _on_dialogue_ended(dialogue_id: String) -> void:
	if dialogue_id == "hermes_intro":
		GameState.set_flag("met_hermes", true)
		var minigame = HERB_MINIGAME.instantiate()
		get_tree().root.add_child(minigame)
		minigame.minigame_completed.connect(GameState.complete_herb_lesson)
	elif dialogue_id == "hermes_epilogue":
		GameState.finish_epilogue()
		AudioController.play_music("epilogue")
