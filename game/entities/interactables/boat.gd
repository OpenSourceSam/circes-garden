extends Area2D

@export var destination: Vector2 = Vector2.ZERO
@export var requires_flag: String = ""

func interact() -> void:
	if requires_flag != "" and not GameState.get_flag(requires_flag):
		# Show message via dialogue box
		var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
		if dialogue_box and not dialogue_box.is_active():
			var d = DialogueData.new()
			d.id = "boat_blocked"
			d.lines = [
				{"speaker": "Circe", "text": "The sea stretches south toward Scylla's strait."},
				{"speaker": "Circe", "text": "I can't go yet. Not without the draught."},
			]
			dialogue_box.start_dialogue(d)
		return
	AudioController.play_sfx("ui_confirm")
	SceneManager.teleport_player(destination)
