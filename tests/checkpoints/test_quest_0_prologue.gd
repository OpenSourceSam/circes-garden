extends RefCounted
## Quest 0: starting a new game leaves the prologue done, quest 1 active and no seeds yet.

func run(gs: Node) -> bool:
	gs.add_item("calming_draught", 1)
	gs.set_flag("quest_4_active", true)
	gs.current_day = 7

	gs.new_game()

	if not gs.get_flag("prologue_complete"):
		push_error("new_game() should set prologue_complete")
		return false
	if not gs.get_flag("quest_1_active"):
		push_error("new_game() should make quest 1 active")
		return false
	if gs.get_flag("quest_4_active") or gs.has_item("calming_draught"):
		push_error("new_game() should clear flags and inventory from an earlier game")
		return false
	if gs.get_item_count("moly_seed") != gs.STARTING_SEEDS:
		push_error("Expected %d starting seeds, got %d" % [gs.STARTING_SEEDS, gs.get_item_count("moly_seed")])
		return false
	if gs.current_day != 1:
		push_error("A new game should start on day 1, got %d" % gs.current_day)
		return false
	return true
