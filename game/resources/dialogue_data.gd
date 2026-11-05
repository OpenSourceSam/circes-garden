extends Resource
class_name DialogueData
## One conversation: an id (printed to the console and passed to dialogue_ended) and its lines.

@export var id: String = ""
@export var lines: Array = []  # [{"speaker": "Hermes", "text": "..."}]; "" speaker is narration
