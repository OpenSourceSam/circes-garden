extends Resource
class_name ItemData
## Defines an item for inventory

@export var id: String = ""
@export var display_name: String = ""
@export var description: String = ""
@export var icon: Texture2D = null
@export var stackable: bool = true
@export var max_stack: int = 99
@export_enum("seed", "crop", "potion", "material") var item_type: String = "material"
