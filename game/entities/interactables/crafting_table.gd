extends Area2D

@onready var status_label: Label = $StatusLabel

func _ready() -> void:
	GameState.flag_changed.connect(_on_flag_changed)
	GameState.inventory_changed.connect(_on_inventory_changed)
	_update_display()

func interact() -> void:
	if not GameState.get_flag("quest_3_active"):
		var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
		if dialogue_box and not dialogue_box.is_active():
			var d = DialogueData.new()
			d.id = "crafting_not_ready"
			d.lines = [
				{"speaker": "Circe", "text": "My old crafting table. Mortar, pestle, vials..."},
				{"speaker": "Circe", "text": "I'll need this later. First, the herbs."},
			]
			dialogue_box.start_dialogue(d)
		return

	if GameState.has_item("moly", 3):
		_craft_calming_draught()
	else:
		var count: int = GameState.get_item_count("moly")
		var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
		if dialogue_box and not dialogue_box.is_active():
			var d = DialogueData.new()
			d.id = "crafting_need_more"
			d.lines = [{"speaker": "Circe", "text": "I need 3 moly to brew the draught. I only have %d." % count}]
			dialogue_box.start_dialogue(d)

func _craft_calming_draught() -> void:
	GameState.remove_item("moly", 3)
	GameState.add_item("calming_draught", 1)
	AudioController.play_sfx("ui_confirm")
	GameState.set_flag("quest_3_complete", true)
	GameState.set_flag("quest_3_active", false)
	GameState.set_flag("quest_4_active", true)
	GameState.set_flag("can_sail_to_scylla", true)

	# Show success dialogue
	var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
	if dialogue_box:
		var d = DialogueData.new()
		d.id = "crafting_success"
		d.lines = [
			{"speaker": "", "text": "*You grind the moly into a fine golden powder.*"},
			{"speaker": "", "text": "*The herbs release a sweet, sharp scent as they dissolve into the draught.*"},
			{"speaker": "Circe", "text": "It's done. The Calming Draught."},
			{"speaker": "Circe", "text": "Now I must sail south and face what I've done."},
		]
		dialogue_box.start_dialogue(d)
	_update_display()

func _on_flag_changed(_f: String, _v: bool) -> void:
	_update_display()

func _on_inventory_changed(_i: String, _q: int) -> void:
	_update_display()

func _update_display() -> void:
	if GameState.get_flag("quest_3_complete"):
		status_label.text = "Draught brewed!"
	elif GameState.get_flag("quest_3_active"):
		var count: int = GameState.get_item_count("moly")
		status_label.text = "Calming Draught\n(%d/3 moly)" % count
	else:
		status_label.text = "Crafting Table"
