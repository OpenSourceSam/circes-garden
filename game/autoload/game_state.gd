extends Node
## GameState - Central state management for Circe's Garden v3
## Simplified for 5-quest demo

# Signals
signal inventory_changed(item_id: String, new_quantity: int)
signal flag_changed(flag: String, value: bool)
signal crop_planted(plot_id: Vector2i, crop_id: String)
signal crop_harvested(plot_id: Vector2i, item_id: String)

# State
var inventory: Dictionary = {}  # { "item_id": quantity }
var quest_flags: Dictionary = {}  # { "flag_name": bool }
var farm_plots: Dictionary = {}  # { Vector2i: plot_data }
var current_day: int = 1

# ============================================
# INITIALIZATION
# ============================================

func _ready() -> void:
	print("[GameState] Initialized")

func new_game() -> void:
	inventory.clear()
	quest_flags.clear()
	farm_plots.clear()
	current_day = 1

	# Starting items
	add_item("moly_seed", 3)

	# Initial flags
	set_flag("prologue_complete", true)
	set_flag("quest_1_active", true)

	print("[GameState] New game started")

# ============================================
# INVENTORY
# ============================================

func add_item(item_id: String, quantity: int = 1) -> void:
	if not inventory.has(item_id):
		inventory[item_id] = 0
	inventory[item_id] += quantity
	inventory_changed.emit(item_id, inventory[item_id])
	print("[GameState] Added %d x %s" % [quantity, item_id])

func remove_item(item_id: String, quantity: int = 1) -> bool:
	if not has_item(item_id, quantity):
		return false
	inventory[item_id] -= quantity
	if inventory[item_id] <= 0:
		inventory.erase(item_id)
	inventory_changed.emit(item_id, inventory.get(item_id, 0))
	return true

func has_item(item_id: String, quantity: int = 1) -> bool:
	return inventory.get(item_id, 0) >= quantity

func get_item_count(item_id: String) -> int:
	return inventory.get(item_id, 0)

# ============================================
# QUEST FLAGS
# ============================================

func set_flag(flag: String, value: bool = true) -> void:
	quest_flags[flag] = value
	flag_changed.emit(flag, value)
	print("[GameState] Flag: %s = %s" % [flag, value])

func get_flag(flag: String) -> bool:
	return quest_flags.get(flag, false)

# ============================================
# FARMING (Simplified)
# ============================================

func plant_crop(position: Vector2i, crop_id: String) -> void:
	farm_plots[position] = {
		"crop_id": crop_id,
		"planted_day": current_day,
		"stage": 0,
		"ready": false
	}
	crop_planted.emit(position, crop_id)

func harvest_crop(position: Vector2i) -> void:
	if not farm_plots.has(position):
		return
	var plot = farm_plots[position]
	if not plot.get("ready", false):
		return

	# Moly harvests as moly
	var harvest_id: String = plot["crop_id"]
	add_item(harvest_id, 1)
	farm_plots.erase(position)
	crop_harvested.emit(position, harvest_id)

func advance_day() -> void:
	current_day += 1
	# Update crop growth
	for pos in farm_plots:
		var plot = farm_plots[pos]
		var days_growing = current_day - plot["planted_day"]
		# Moly takes 3 days to mature
		if days_growing >= 3:
			plot["ready"] = true
			plot["stage"] = 3
		else:
			plot["stage"] = days_growing
	print("[GameState] Day %d" % current_day)
