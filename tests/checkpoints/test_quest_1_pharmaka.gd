extends RefCounted
## Quest 1: winning the herb lesson closes quest 1, opens quest 2 and adds Hermes's seeds.

func run(gs: Node) -> bool:
	gs.new_game()

	gs.complete_herb_lesson()

	if not gs.get_flag("herb_minigame_complete") or not gs.get_flag("quest_1_complete"):
		push_error("The herb lesson should mark herb_minigame_complete and quest_1_complete")
		return false
	if gs.get_flag("quest_1_active") or not gs.get_flag("quest_2_active"):
		push_error("Quest 1 should close and quest 2 open")
		return false
	var expected_seeds: int = gs.STARTING_SEEDS + gs.HERB_LESSON_SEEDS
	if gs.get_item_count("moly_seed") != expected_seeds:
		push_error("Expected %d seeds, got %d" % [expected_seeds, gs.get_item_count("moly_seed")])
		return false
	return true
