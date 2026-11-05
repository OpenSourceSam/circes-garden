extends "res://game/entities/npcs/wandering_npc.gd"
## Scylla in her cove. Before quest 4 she is only described. With the Calming Draught,
## Circe tries the cure and it fails, as in the novel.

const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const WorldLabel := preload("res://game/util/world_label.gd")

@onready var label: Label = $Label

func _ready() -> void:
	super()
	WorldLabel.setup(label, -100.0)

func prompt_text() -> String:
	return "Face Scylla" if GameState.get_flag("quest_4_active") else "Look at Scylla"

func world_label() -> Label:
	return label

func interact() -> void:
	if not GameState.get_flag("quest_4_active"):
		DialogueBox.open(self, "scylla_not_ready")
	elif GameState.give_draught_to_scylla():
		DialogueBox.open(self, "scylla_cure_attempt")
		label.text = "Scylla\n(unchanged)"
	else:
		DialogueBox.open(self, "scylla_no_potion")
