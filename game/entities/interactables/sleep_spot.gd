extends Area2D

@onready var day_label: Label = $DayLabel

var _sleep_thoughts: Array = [
	[
		{"speaker": "", "text": "*Night falls over Aiaia. The stars wheel overhead.*"},
		{"speaker": "Circe", "text": "Another day. The herbs will grow while I sleep."},
	],
	[
		{"speaker": "", "text": "*You dream of Scylla — before. Her laugh, her dark hair.*"},
		{"speaker": "", "text": "*Then the dream shifts. Six heads. Screaming.*"},
		{"speaker": "Circe", "text": "...I have to keep going."},
	],
	[
		{"speaker": "", "text": "*The night is quiet. Only the sound of waves.*"},
		{"speaker": "Circe", "text": "How many nights have I spent on this island, alone with my guilt?"},
	],
	[
		{"speaker": "", "text": "*Sleep comes fitfully. You toss and turn.*"},
		{"speaker": "Circe", "text": "Soon. The moly will be ready soon."},
	],
	[
		{"speaker": "", "text": "*The wind carries a distant sound. Something between a howl and a cry.*"},
		{"speaker": "Circe", "text": "I hear you, Scylla. Hold on."},
	],
]

func _ready() -> void:
	day_label.text = "Rest (Day %d)" % GameState.current_day

func interact() -> void:
	# Show a sleep thought before advancing the day
	var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
	if dialogue_box and not dialogue_box.is_active():
		var thought_index: int = (GameState.current_day - 1) % _sleep_thoughts.size()
		var d = DialogueData.new()
		d.id = "sleep_day_%d" % GameState.current_day
		d.lines = _sleep_thoughts[thought_index]
		dialogue_box.start_dialogue(d)

		# Advance day after dialogue ends
		if not dialogue_box.dialogue_ended.is_connected(_on_sleep_dialogue_ended):
			dialogue_box.dialogue_ended.connect(_on_sleep_dialogue_ended)
	else:
		# Fallback if dialogue box unavailable
		_advance()

func _on_sleep_dialogue_ended(_dialogue_id: String) -> void:
	var dialogue_box = get_tree().get_first_node_in_group("dialogue_box")
	if dialogue_box and dialogue_box.dialogue_ended.is_connected(_on_sleep_dialogue_ended):
		dialogue_box.dialogue_ended.disconnect(_on_sleep_dialogue_ended)
	_advance()

func _advance() -> void:
	GameState.advance_day()
	AudioController.play_sfx("ui_confirm")
	day_label.text = "Rest (Day %d)" % GameState.current_day
	# Tell farm plots to refresh their display
	get_tree().call_group("farm_plots", "_update_display")
