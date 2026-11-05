extends "res://game/entities/npcs/wandering_npc.gd"
## Scylla in her cove. Before quest 4 she is only described. With the Calming Draught,
## Circe tries the cure and it fails, as in the novel.

const DialogueBox := preload("res://game/ui/dialogue_box.gd")

@onready var label: Label = $Label

func interact() -> void:
	if not GameState.get_flag("quest_4_active"):
		DialogueBox.open(self, "scylla_not_ready")
	elif GameState.give_draught_to_scylla():
		DialogueBox.open(self, "scylla_cure_attempt")
		label.text = "Scylla\n(unchanged)"
	else:
		DialogueBox.open(self, "scylla_no_potion")
