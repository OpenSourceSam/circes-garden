extends Area2D
## Circe's table, where three moly become the Calming Draught (quest 3).

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const StoryText := preload("res://game/data/story_text.gd")
const WorldLabel := preload("res://game/util/world_label.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const CRAFTING_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/crafting_table.png"

@onready var sprite: Sprite2D = $Sprite
@onready var status_label: Label = $StatusLabel

func _ready() -> void:
	WorldLabel.setup(status_label, 22.0, false)
	sprite.texture = TextureLoaderUtil.load_texture(CRAFTING_TEXTURE_PATH)
	GameState.flag_changed.connect(_on_flag_changed)
	GameState.inventory_changed.connect(_on_inventory_changed)
	_update_display()

func interact() -> void:
	if not GameState.get_flag("quest_3_active"):
		DialogueBox.open(self, "crafting_not_ready")
	elif GameState.brew_calming_draught():
		AudioController.play_sfx("ui_confirm")
		DialogueBox.open(self, "crafting_success")
	else:
		var lines: Array = StoryText.LINES["crafting_need_more"].duplicate(true)
		lines[0]["text"] = lines[0]["text"] % GameState.get_item_count("moly")
		DialogueBox.open(self, "crafting_need_more", lines)

func prompt_text() -> String:
	if GameState.get_flag("quest_3_active"):
		return "Brew the Calming Draught"
	return "Your worktable"

func world_label() -> Label:
	return status_label

func _on_flag_changed(_flag: String, _value: bool) -> void:
	_update_display()

func _on_inventory_changed(_item_id: String, _quantity: int) -> void:
	_update_display()

func _update_display() -> void:
	if GameState.get_flag("quest_3_complete"):
		status_label.text = "Draught brewed!"
	elif GameState.get_flag("quest_3_active"):
		status_label.text = "Calming Draught\n(%d/%d moly)" % [GameState.get_item_count("moly"), GameState.MOLY_PER_DRAUGHT]
	else:
		status_label.text = "Crafting Table"
