extends Resource
class_name DialogueData
## Defines a dialogue sequence for Circe's Garden

@export var id: String = ""
@export var lines: Array = []  # [{"speaker": "Hermes", "text": "Hello!", "emotion": "amused"}]
@export var choices: Array = []  # [{"text": "Yes", "next_id": "accept"}]
@export var flags_required: Array = []
@export var flags_to_set: Array = []
@export var next_dialogue_id: String = ""
