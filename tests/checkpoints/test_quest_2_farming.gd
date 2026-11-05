extends RefCounted
## Quest 2: three planted seeds ripen after three nights; the third harvest opens quest 3.

const PLOTS := [Vector2i(0, 0), Vector2i(1, 0), Vector2i(2, 0)]

func run(gs: Node) -> bool:
	gs.new_game()
	gs.complete_herb_lesson()
	var seeds_before: int = gs.get_item_count("moly_seed")

	for plot in PLOTS:
		if not gs.plant_seed(plot):
			push_error("plant_seed(%s) should succeed with seeds in hand" % plot)
			return false
	if gs.plant_seed(PLOTS[0]):
		push_error("plant_seed() should refuse a plot that is already planted")
		return false
	if gs.get_item_count("moly_seed") != seeds_before - PLOTS.size():
		push_error("Each planting should use one seed")
		return false

	for _night in gs.DAYS_TO_MATURE - 1:
		gs.advance_day()
	gs.harvest_crop(PLOTS[0])
	if gs.get_item_count("moly") != 0:
		push_error("Moly should not be harvestable before day %d" % (1 + gs.DAYS_TO_MATURE))
		return false
	gs.advance_day()

	gs.harvest_crop(PLOTS[0])
	gs.harvest_crop(PLOTS[1])
	if gs.get_flag("quest_3_active"):
		push_error("Two moly should not finish quest 2")
		return false
	gs.harvest_crop(PLOTS[2])

	if gs.get_item_count("moly") != gs.MOLY_PER_DRAUGHT:
		push_error("Expected %d moly, got %d" % [gs.MOLY_PER_DRAUGHT, gs.get_item_count("moly")])
		return false
	if not gs.farm_plots.is_empty():
		push_error("Harvested plots should be empty")
		return false
	if not gs.get_flag("quest_2_complete") or gs.get_flag("quest_2_active") or not gs.get_flag("quest_3_active"):
		push_error("The third harvest should close quest 2 and open quest 3")
		return false
	return true
