extends RefCounted
## Checkpoint test for Quest 2: Farm Moly
## Verifies: Planted seeds, time passed, harvested moly, quest 3 activates

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	# Setup: Start from Quest 1 complete
	gs.new_game()
	gs.set_flag("quest_1_complete", true)
	gs.set_flag("quest_2_active", true)
	gs.add_item("moly_seed", 5)

	# Simulate Quest 2:
	# - Plant moly seeds
	# - Wait 3 days for growth
	# - Harvest moly

	# Plant 3 moly seeds
	gs.remove_item("moly_seed", 3)
	gs.plant_crop(Vector2i(0, 0), "moly")
	gs.plant_crop(Vector2i(1, 0), "moly")
	gs.plant_crop(Vector2i(2, 0), "moly")

	# Advance 3 days
	gs.advance_day()  # Day 2
	gs.advance_day()  # Day 3
	gs.advance_day()  # Day 4 - ready

	# Harvest all
	gs.harvest_crop(Vector2i(0, 0))
	gs.harvest_crop(Vector2i(1, 0))
	gs.harvest_crop(Vector2i(2, 0))

	# Mark quest complete
	gs.set_flag("quest_2_complete", true)
	gs.set_flag("quest_2_active", false)
	gs.set_flag("quest_3_active", true)

	# CHECKPOINT ASSERTIONS

	# 1. Should have harvested moly (not seeds - the actual herb)
	if gs.get_item_count("moly") < 3:
		push_error("Should have at least 3 moly from harvest, got %d" % gs.get_item_count("moly"))
		return false

	# 2. Farm plots should be empty after harvest
	if gs.farm_plots.size() > 0:
		push_error("Farm plots should be empty after harvest")
		return false

	# 3. Quest 2 complete
	if not gs.get_flag("quest_2_complete"):
		push_error("Quest 2 should be complete")
		return false

	# 4. Quest 3 active
	if not gs.get_flag("quest_3_active"):
		push_error("Quest 3 should be active")
		return false

	# 5. Time should have passed
	if gs.current_day < 4:
		push_error("At least 4 days should have passed")
		return false

	print("  └─ Farmed moly, harvested 3+, Quest 3 active, day %d" % gs.current_day)
	return true
