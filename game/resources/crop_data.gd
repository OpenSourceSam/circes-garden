extends Resource
class_name CropData
## Defines a crop type for farming

@export var id: String = ""
@export var display_name: String = ""
@export var seed_item_id: String = ""
@export var harvest_item_id: String = ""
@export var days_to_mature: int = 3
@export var growth_stages: Array[Texture2D] = []
@export var regrows: bool = false
