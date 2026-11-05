extends RefCounted
## Quest 4: the draught is used up and fails; Scylla stays a monster, as in the novel.

func run(gs: Node) -> bool:
	gs.new_game()
	gs.set_flag("quest_4_active", true)
	if gs.give_draught_to_scylla():
		push_error("Without a draught there is nothing to give")
		return false

	gs.add_item("calming_draught", 1)
	if not gs.give_draught_to_scylla():
		push_error("Giving the draught should succeed in quest 4")
		return false
	if gs.has_item("calming_draught"):
		push_error("The draught should be used up")
		return false
	if not gs.get_flag("potion_failed") or gs.get_flag("scylla_cured"):
		push_error("The cure must fail: potion_failed set, scylla_cured not set")
		return false
	if not gs.get_flag("quest_4_complete") or gs.get_flag("quest_4_active") or not gs.get_flag("quest_5_active"):
		push_error("Giving the draught should close quest 4 and open quest 5")
		return false
	return true
