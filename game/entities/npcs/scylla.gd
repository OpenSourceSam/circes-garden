extends CharacterBody2D

@onready var sprite: Sprite2D = $Sprite
@onready var label: Label = $Label

func _ready() -> void:
	collision_layer = 1
	collision_mask = 0

func interact() -> void:
	if not GameState.get_flag("quest_4_active"):
		# Not time yet - describe the distant monster
		var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
		if dialogue_box and not dialogue_box.is_active():
			var d = DialogueData.new()
			d.id = "scylla_not_ready"
			d.lines = [
				{"speaker": "", "text": "*Something writhes in the darkness ahead. Six heads, weaving.*"},
				{"speaker": "", "text": "*A low, guttural sound echoes off the rocks.*"},
				{"speaker": "Circe", "text": "Scylla... what have I done to you?"},
				{"speaker": "Circe", "text": "I need to prepare before I face her."},
			]
			dialogue_box.start_dialogue(d)
		return

	if GameState.has_item("calming_draught"):
		_attempt_cure()
	else:
		var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
		if dialogue_box and not dialogue_box.is_active():
			var d = DialogueData.new()
			d.id = "scylla_no_potion"
			d.lines = [
				{"speaker": "Circe", "text": "I need the Calming Draught. I can't face her empty-handed."},
				{"speaker": "Circe", "text": "I should go back and brew it first."},
			]
			dialogue_box.start_dialogue(d)

func _attempt_cure() -> void:
	# Consume potion
	GameState.remove_item("calming_draught", 1)

	# CRITICAL: Potion FAILS (book-accurate ending)
	GameState.set_flag("attempted_cure", true)
	GameState.set_flag("potion_failed", true)
	GameState.set_flag("scylla_cured", false)

	# Complete quest 4
	GameState.set_flag("quest_4_complete", true)
	GameState.set_flag("quest_4_active", false)
	GameState.set_flag("quest_5_active", true)

	# Show failure dialogue
	var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
	if dialogue_box:
		var d = DialogueData.new()
		d.id = "scylla_cure_attempt"
		d.lines = [
			{"speaker": "Circe", "text": "Scylla... it's me. Circe."},
			{"speaker": "", "text": "*The six heads turn. Twelve eyes stare, empty of recognition.*"},
			{"speaker": "Circe", "text": "I know you're in there. I brought something that might help."},
			{"speaker": "", "text": "*You hold out the Calming Draught with trembling hands.*"},
			{"speaker": "", "text": "*For a moment, one head tilts — curious, almost gentle.*"},
			{"speaker": "", "text": "*Then — SHRIEEEEK!*"},
			{"speaker": "", "text": "*Scylla swipes. The vial shatters against the rocks.*"},
			{"speaker": "", "text": "*The draught pools on the stone, useless. The monster writhes on, unchanged.*"},
			{"speaker": "Circe", "text": "No... no, please..."},
			{"speaker": "Circe", "text": "I did this to you. I thought I could undo it."},
			{"speaker": "", "text": "*She doesn't hear you. She was never going to hear you.*"},
			{"speaker": "Circe", "text": "I'm sorry, Scylla. I'm so sorry."},
		]
		dialogue_box.start_dialogue(d)

	# Visual feedback
	label.text = "Scylla\n(unchanged)"
