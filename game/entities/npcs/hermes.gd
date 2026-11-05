extends "res://game/entities/npcs/wandering_npc.gd"
## Hermes on the terrace. What he says follows the quest; his first talk opens the herb
## lesson and his last one ends the game.

const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const WorldLabel := preload("res://game/util/world_label.gd")
const HERB_MINIGAME := preload("res://game/scenes/herb_minigame.tscn")

func _ready() -> void:
	super()
	WorldLabel.setup($Label, -46.0)

func prompt_text() -> String:
	return "Talk to Hermes"

func world_label() -> Label:
	return $Label

func interact() -> void:
	var box = DialogueBox.open(self, _current_dialogue_id())
	if box and not box.dialogue_ended.is_connected(_on_dialogue_ended):
		box.dialogue_ended.connect(_on_dialogue_ended)

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

func _on_dialogue_ended(dialogue_id: String) -> void:
	if dialogue_id == "hermes_intro":
		GameState.set_flag("met_hermes", true)
		var minigame = HERB_MINIGAME.instantiate()
		get_tree().root.add_child(minigame)
		minigame.minigame_completed.connect(GameState.complete_herb_lesson)
	elif dialogue_id == "hermes_epilogue":
		GameState.finish_epilogue()
		AudioController.play_music("epilogue")
