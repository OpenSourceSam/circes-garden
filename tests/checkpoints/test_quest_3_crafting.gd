extends RefCounted
## Quest 3: the draught needs quest 3 and three moly; brewing it opens quest 4 and the boat.

func run(gs: Node) -> bool:
	gs.new_game()
	gs.add_item("moly", gs.MOLY_PER_DRAUGHT)
	if gs.brew_calming_draught():
		push_error("Brewing should wait for quest 3")
		return false

	gs.set_flag("quest_3_active", true)
	gs.remove_item("moly", 1)
	if gs.brew_calming_draught():
		push_error("Brewing should need %d moly" % gs.MOLY_PER_DRAUGHT)
		return false

	gs.add_item("moly", 1)
	if not gs.brew_calming_draught():
		push_error("Brewing should succeed in quest 3 with enough moly")
		return false
	if gs.get_item_count("calming_draught") != 1 or gs.get_item_count("moly") != 0:
		push_error("Brewing should turn the moly into one draught")
		return false
	if not gs.get_flag("quest_3_complete") or gs.get_flag("quest_3_active") or not gs.get_flag("quest_4_active"):
		push_error("Brewing should close quest 3 and open quest 4")
		return false
	if not gs.get_flag("can_sail_to_scylla"):
		push_error("Brewing should unlock the boat to Scylla")
		return false
	return true
