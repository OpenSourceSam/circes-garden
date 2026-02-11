extends CharacterBody2D

func _ready() -> void:
	collision_layer = 1
	collision_mask = 0

func interact() -> void:
	var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
	if not dialogue_box or dialogue_box.is_active():
		return

	var dialogue: DialogueData = _get_current_dialogue()
	if dialogue:
		dialogue_box.start_dialogue(dialogue)
		if not dialogue_box.dialogue_ended.is_connected(_on_dialogue_ended):
			dialogue_box.dialogue_ended.connect(_on_dialogue_ended)

func _get_current_dialogue() -> DialogueData:
	if not GameState.get_flag("met_hermes"):
		return _create_intro_dialogue()
	elif GameState.get_flag("quest_5_active"):
		return _create_epilogue_dialogue()
	elif GameState.get_flag("quest_4_active"):
		return _create_sailing_hint()
	elif GameState.get_flag("quest_3_active"):
		return _create_crafting_hint()
	elif GameState.get_flag("quest_2_active"):
		return _create_farming_hint()
	else:
		return _create_default_dialogue()

func _on_dialogue_ended(dialogue_id: String) -> void:
	if dialogue_id == "hermes_intro":
		_launch_herb_minigame()
	elif dialogue_id == "hermes_epilogue":
		AudioController.play_music("epilogue")

func _launch_herb_minigame() -> void:
	var minigame = preload("res://game/scenes/herb_minigame.tscn").instantiate()
	get_tree().root.add_child(minigame)
	minigame.minigame_completed.connect(_on_minigame_completed)

func _on_minigame_completed() -> void:
	GameState.add_item("moly_seed", 5)
	GameState.set_flag("herb_minigame_complete", true)
	GameState.set_flag("quest_1_complete", true)
	GameState.set_flag("quest_1_active", false)
	GameState.set_flag("quest_2_active", true)

func _create_intro_dialogue() -> DialogueData:
	var d = DialogueData.new()
	d.id = "hermes_intro"
	d.lines = [
		{"speaker": "Hermes", "text": "Well, well. The witch of Aiaia. You look terrible."},
		{"speaker": "Circe", "text": "I need your help, Hermes."},
		{"speaker": "Hermes", "text": "Let me guess - Scylla? You want to undo what you did."},
		{"speaker": "Circe", "text": "I have to try. Tell me about the healing herbs."},
		{"speaker": "Hermes", "text": "Fine. But first, show me you can tell moly from nightshade."}
	]
	d.flags_to_set = ["met_hermes"]
	return d

func _create_epilogue_dialogue() -> DialogueData:
	var d = DialogueData.new()
	d.id = "hermes_epilogue"
	d.lines = [
		{"speaker": "Circe", "text": "The potion failed. She wouldn't take it."},
		{"speaker": "Hermes", "text": "I did warn you. Some things cannot be undone."},
		{"speaker": "Circe", "text": "I know that now."},
		{"speaker": "Hermes", "text": "So what now?"},
		{"speaker": "Circe", "text": "I tend my garden. I live with what I've done."},
		{"speaker": "Hermes", "text": "That might be the wisest thing you've ever said."}
	]
	d.flags_to_set = [
		"returned_to_aiaia",
		"epilogue_dialogue_complete",
		"found_peace",
		"quest_5_complete",
		"game_complete"
	]
	return d

func _create_farming_hint() -> DialogueData:
	var d = DialogueData.new()
	d.id = "hermes_farming"
	d.lines = [
		{"speaker": "Hermes", "text": "Now comes the tedious part. Farming."},
		{"speaker": "Circe", "text": "I know how to grow herbs, Hermes."},
		{"speaker": "Hermes", "text": "Then plant the moly seeds in the plots and sleep to let them grow. Three days should do it."},
		{"speaker": "Hermes", "text": "Patience, witch. Not everything bends to your will immediately."},
	]
	d.flags_to_set = []
	return d

func _create_crafting_hint() -> DialogueData:
	var d = DialogueData.new()
	d.id = "hermes_crafting"
	d.lines = [
		{"speaker": "Hermes", "text": "You've grown the moly. Good."},
		{"speaker": "Hermes", "text": "Now use the crafting table to brew the Calming Draught. You'll need three moly."},
		{"speaker": "Circe", "text": "And this will cure her?"},
		{"speaker": "Hermes", "text": "I said it would calm her. I never said 'cure.'"},
	]
	d.flags_to_set = []
	return d

func _create_sailing_hint() -> DialogueData:
	var d = DialogueData.new()
	d.id = "hermes_sailing"
	d.lines = [
		{"speaker": "Hermes", "text": "You have the draught. The boat is ready."},
		{"speaker": "Circe", "text": "Will this work?"},
		{"speaker": "Hermes", "text": "Honestly? I doubt it. But you won't rest until you try."},
		{"speaker": "Circe", "text": "I have to."},
		{"speaker": "Hermes", "text": "Then go. Sail south. And Circe... be careful."},
	]
	d.flags_to_set = []
	return d

func _create_default_dialogue() -> DialogueData:
	var d = DialogueData.new()
	d.id = "hermes_default"
	d.lines = [
		{"speaker": "Hermes", "text": "Still here? I thought you had work to do."},
		{"speaker": "Circe", "text": "Just thinking."},
		{"speaker": "Hermes", "text": "Dangerous habit for a witch. Get moving."},
	]
	d.flags_to_set = []
	return d
