extends RefCounted
## Quest 5 and the whole chain: every quest step in order, from a new game to game_complete.

func run(gs: Node) -> bool:
	gs.new_game()
	gs.complete_herb_lesson()
	for column in 3:
		gs.plant_seed(Vector2i(column, 0))
	for _night in gs.DAYS_TO_MATURE:
		gs.advance_day()
	for column in 3:
		gs.harvest_crop(Vector2i(column, 0))
	if not gs.brew_calming_draught():
		push_error("The chain should reach a brewed draught")
		return false
	if not gs.give_draught_to_scylla():
		push_error("The chain should reach Scylla with the draught")
		return false

	gs.finish_epilogue()

	for quest in range(1, 6):
		if not gs.get_flag("quest_%d_complete" % quest):
			push_error("Quest %d should be complete" % quest)
			return false
		if gs.get_flag("quest_%d_active" % quest):
			push_error("Quest %d should not be active at the end" % quest)
			return false
	if not gs.get_flag("game_complete") or not gs.get_flag("found_peace"):
		push_error("The epilogue should set game_complete and found_peace")
		return false
	if not gs.get_flag("potion_failed") or gs.get_flag("scylla_cured"):
		push_error("The ending must keep the failed cure")
		return false
	if gs.current_day != 1 + gs.DAYS_TO_MATURE:
		push_error("Expected day %d at the end, got %d" % [1 + gs.DAYS_TO_MATURE, gs.current_day])
		return false
	return true
