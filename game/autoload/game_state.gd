extends Node
## Inventory, quest flags, farm plots and the day counter. The quest steps that
## change several of these at once live here too, so the headless tests can run
## them without a scene.

const DAYS_TO_MATURE := 3
## Circe starts with no seeds: Hermes gives her exactly one per plot after the herb lesson.
const STARTING_SEEDS := 0
const HERB_LESSON_SEEDS := 3
const MOLY_PER_DRAUGHT := 3

signal inventory_changed(item_id: String, new_quantity: int)
signal flag_changed(flag: String, value: bool)
signal crop_planted(plot_id: Vector2i, crop_id: String)
signal crop_harvested(plot_id: Vector2i, item_id: String)
signal day_advanced(new_day: int)

var inventory: Dictionary = {}  # { "item_id": quantity }
var quest_flags: Dictionary = {}  # { "flag_name": bool }
var farm_plots: Dictionary = {}  # { Vector2i: plot_data }
var current_day: int = 1

# ============================================
# INITIALIZATION
# ============================================

func _ready() -> void:
	_ensure_controller_bindings()
	print("[GameState] Initialized")

## The input map in project.godot lists keyboard keys only. This adds the controller's
## A, B and d-pad buttons to the same actions, skipping any that are already bound.
func _ensure_controller_bindings() -> void:
	_bind_joypad_button("interact", JOY_BUTTON_A)
	_bind_joypad_button("ui_accept", JOY_BUTTON_A)
	_bind_joypad_button("ui_cancel", JOY_BUTTON_B)
	_bind_joypad_button("ui_left", JOY_BUTTON_DPAD_LEFT)
	_bind_joypad_button("ui_right", JOY_BUTTON_DPAD_RIGHT)
	_bind_joypad_button("ui_up", JOY_BUTTON_DPAD_UP)
	_bind_joypad_button("ui_down", JOY_BUTTON_DPAD_DOWN)

func _bind_joypad_button(action_name: String, button_index: int) -> void:
	if not InputMap.has_action(action_name):
		return
	if _action_has_joypad_button(action_name, button_index):
		return

	var event := InputEventJoypadButton.new()
	event.button_index = button_index
	InputMap.action_add_event(action_name, event)

func _action_has_joypad_button(action_name: String, button_index: int) -> bool:
	for event in InputMap.action_get_events(action_name):
		if event is InputEventJoypadButton and event.button_index == button_index:
			return true
	return false

func new_game() -> void:
	inventory.clear()
	quest_flags.clear()
	farm_plots.clear()
	current_day = 1

	if STARTING_SEEDS > 0:
		add_item("moly_seed", STARTING_SEEDS)
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
# FARMING
# ============================================

## Plants one moly seed from the inventory. False when the plot is taken or there is no seed.
func plant_seed(position: Vector2i) -> bool:
	if farm_plots.has(position) or not has_item("moly_seed"):
		return false
	remove_item("moly_seed", 1)
	plant_crop(position, "moly")
	return true

func plant_crop(position: Vector2i, crop_id: String) -> void:
	farm_plots[position] = {
		"crop_id": crop_id,
		"planted_day": current_day,
		"stage": 0,
		"ready": false
	}
	print("[GameState] Planted %s at %s" % [crop_id, position])
	crop_planted.emit(position, crop_id)

func harvest_crop(position: Vector2i) -> void:
	if not farm_plots.has(position):
		return
	var plot = farm_plots[position]
	if not plot.get("ready", false):
		return

	var harvest_id: String = plot["crop_id"]
	add_item(harvest_id, 1)
	farm_plots.erase(position)
	print("[GameState] Harvested %s at %s" % [harvest_id, position])
	crop_harvested.emit(position, harvest_id)
	if get_flag("quest_2_active") and get_item_count("moly") >= MOLY_PER_DRAUGHT:
		set_flag("quest_2_complete", true)
		set_flag("quest_2_active", false)
		set_flag("quest_3_active", true)

func advance_day() -> void:
	current_day += 1
	for pos in farm_plots:
		var plot: Dictionary = farm_plots[pos]
		var days_growing: int = current_day - plot["planted_day"]
		plot["stage"] = mini(days_growing, DAYS_TO_MATURE)
		plot["ready"] = days_growing >= DAYS_TO_MATURE
	day_advanced.emit(current_day)
	print("[GameState] Day %d" % current_day)

# ============================================
# QUEST STEPS
# ============================================

## Quest 1 ends when the herb lesson is won: Hermes hands over more seeds.
func complete_herb_lesson() -> void:
	add_item("moly_seed", HERB_LESSON_SEEDS)
	set_flag("herb_minigame_complete", true)
	set_flag("quest_1_complete", true)
	set_flag("quest_1_active", false)
	set_flag("quest_2_active", true)

## Quest 3: three moly become one Calming Draught. False when it is not time or moly is short.
func brew_calming_draught() -> bool:
	if not get_flag("quest_3_active") or not has_item("moly", MOLY_PER_DRAUGHT):
		return false
	remove_item("moly", MOLY_PER_DRAUGHT)
	add_item("calming_draught", 1)
	set_flag("quest_3_complete", true)
	set_flag("quest_3_active", false)
	set_flag("quest_4_active", true)
	set_flag("can_sail_to_scylla", true)
	return true

## Quest 4: the draught calms Scylla for one breath and then fails, as in the novel.
func give_draught_to_scylla() -> bool:
	if not get_flag("quest_4_active") or not has_item("calming_draught"):
		return false
	remove_item("calming_draught", 1)
	set_flag("attempted_cure", true)
	set_flag("potion_failed", true)
	set_flag("scylla_cured", false)
	set_flag("quest_4_complete", true)
	set_flag("quest_4_active", false)
	set_flag("quest_5_active", true)
	return true

## Quest 5 ends after the last talk with Hermes; setting game_complete rolls the credits.
func finish_epilogue() -> void:
	set_flag("returned_to_aiaia", true)
	set_flag("epilogue_dialogue_complete", true)
	set_flag("found_peace", true)
	set_flag("quest_5_complete", true)
	set_flag("quest_5_active", false)
	set_flag("game_complete", true)
