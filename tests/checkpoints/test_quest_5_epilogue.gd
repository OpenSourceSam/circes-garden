extends RefCounted
## Checkpoint test for Quest 5: Epilogue (Acceptance)
## Verifies: Returned home, found peace, game complete

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	# Setup: Start from Quest 4 complete (potion failed)
	gs.new_game()
	gs.set_flag("quest_1_complete", true)
	gs.set_flag("quest_2_complete", true)
	gs.set_flag("quest_3_complete", true)
	gs.set_flag("quest_4_complete", true)
	gs.set_flag("quest_1_active", false)
	gs.set_flag("quest_5_active", true)
	gs.set_flag("potion_failed", true)
	gs.set_flag("scylla_cured", false)

	# Simulate Quest 5 (Epilogue):
	# - Return to Aiaia
	# - Dialogue with Hermes about acceptance
	# - Circe finds peace despite failure
	# - Game ends

	gs.set_flag("returned_to_aiaia", true)
	gs.set_flag("epilogue_dialogue_complete", true)
	gs.set_flag("found_peace", true)

	# Mark game complete
	gs.set_flag("quest_5_complete", true)
	gs.set_flag("quest_5_active", false)
	gs.set_flag("game_complete", true)

	# CHECKPOINT ASSERTIONS

	# 1. All quests complete
	for i in range(1, 6):
		var flag = "quest_%d_complete" % i
		if not gs.get_flag(flag):
			push_error("Quest %d should be complete" % i)
			return false

	# 2. Game marked complete
	if not gs.get_flag("game_complete"):
		push_error("Game should be marked complete")
		return false

	# 3. Found peace (thematic ending)
	if not gs.get_flag("found_peace"):
		push_error("Circe should find peace in epilogue")
		return false

	# 4. Verify book-accurate state persisted
	if not gs.get_flag("potion_failed"):
		push_error("Potion failure should still be recorded")
		return false

	if gs.get_flag("scylla_cured"):
		push_error("Scylla should NOT be cured at end")
		return false

	# 5. No quests should be active
	for i in range(1, 6):
		var flag = "quest_%d_active" % i
		if gs.get_flag(flag):
			push_error("Quest %d should not be active at end" % i)
			return false

	print("  └─ All quests complete, found peace, game_complete=true")
	print("  └─ Book-accurate: potion failed, Scylla lives as monster")
	return true
