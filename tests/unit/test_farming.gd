extends RefCounted
## Unit tests for GameState farming system

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	var all_passed := true

	all_passed = _test_plant_crop() and all_passed
	all_passed = _test_crop_growth() and all_passed
	all_passed = _test_harvest_crop() and all_passed

	return all_passed

func _test_plant_crop() -> bool:
	gs.farm_plots.clear()
	gs.current_day = 1

	var plot_pos := Vector2i(0, 0)
	gs.plant_crop(plot_pos, "moly")

	if not gs.farm_plots.has(plot_pos):
		push_error("plant_crop: Plot should exist")
		return false

	var plot = gs.farm_plots[plot_pos]
	if plot["crop_id"] != "moly":
		push_error("plant_crop: Wrong crop_id")
		return false

	if plot["planted_day"] != 1:
		push_error("plant_crop: Wrong planted_day")
		return false

	if plot["stage"] != 0:
		push_error("plant_crop: Should start at stage 0")
		return false

	if plot["ready"] != false:
		push_error("plant_crop: Should not be ready immediately")
		return false

	return true

func _test_crop_growth() -> bool:
	gs.farm_plots.clear()
	gs.current_day = 1
	gs.inventory.clear()

	var plot_pos := Vector2i(1, 1)
	gs.plant_crop(plot_pos, "moly")

	# Day 2
	gs.advance_day()
	var plot = gs.farm_plots[plot_pos]
	if plot["stage"] != 1:
		push_error("crop_growth: Day 2 should be stage 1, got %d" % plot["stage"])
		return false

	# Day 3
	gs.advance_day()
	plot = gs.farm_plots[plot_pos]
	if plot["stage"] != 2:
		push_error("crop_growth: Day 3 should be stage 2, got %d" % plot["stage"])
		return false

	# Day 4 (moly takes 3 days)
	gs.advance_day()
	plot = gs.farm_plots[plot_pos]
	if plot["stage"] != 3:
		push_error("crop_growth: Day 4 should be stage 3, got %d" % plot["stage"])
		return false

	if not plot["ready"]:
		push_error("crop_growth: Should be ready after 3 days")
		return false

	return true

func _test_harvest_crop() -> bool:
	gs.farm_plots.clear()
	gs.inventory.clear()
	gs.current_day = 1

	var plot_pos := Vector2i(2, 2)
	gs.plant_crop(plot_pos, "moly")

	# Try harvest before ready - should do nothing
	gs.harvest_crop(plot_pos)
	if not gs.farm_plots.has(plot_pos):
		push_error("harvest_crop: Should not harvest unready crop")
		return false

	# Advance to ready
	gs.advance_day()  # day 2
	gs.advance_day()  # day 3
	gs.advance_day()  # day 4 - ready

	# Now harvest
	gs.harvest_crop(plot_pos)

	if gs.farm_plots.has(plot_pos):
		push_error("harvest_crop: Plot should be removed after harvest")
		return false

	if gs.get_item_count("moly") != 1:
		push_error("harvest_crop: Should have 1 moly in inventory")
		return false

	return true
