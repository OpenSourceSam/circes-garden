extends Area2D
## Circe's table, where three moly become the Calming Draught (quest 3).

const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const StoryText := preload("res://game/data/story_text.gd")
const DialogueBox := preload("res://game/ui/dialogue_box.gd")
const CRAFTING_TEXTURE_PATH := "res://assets/image_pipeline/generated/raw/sprites/entities/crafting_table.png"

@onready var sprite: Sprite2D = $Sprite

func _ready() -> void:
	preload("res://game/util/ground_shadow.gd").attach(self, Vector2(0, 23), Vector2(24, 6))
	sprite.texture = TextureLoaderUtil.load_texture(CRAFTING_TEXTURE_PATH)

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

## No floating label: what the table is for, and how much moly Circe has, show in the prompt.
func prompt_text() -> String:
	if GameState.get_flag("quest_3_complete"):
		return "Look at your worktable"
	if GameState.get_flag("quest_3_active"):
		return "Brew the Calming Draught (%d/%d moly)" % [GameState.get_item_count("moly"), GameState.MOLY_PER_DRAUGHT]
	return "Look at your worktable"

func world_label() -> Label:
	return null
