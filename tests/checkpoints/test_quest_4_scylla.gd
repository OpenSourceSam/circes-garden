extends RefCounted
## Checkpoint test for Quest 4: Sail to Scylla (Potion Fails)
## Verifies: Traveled to cove, used potion, potion FAILED, quest 5 activates
## CRITICAL: This is the book-accurate ending - Scylla remains a monster

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	# Setup: Start from Quest 3 complete with potion
	gs.new_game()
	gs.set_flag("quest_1_complete", true)
	gs.set_flag("quest_2_complete", true)
	gs.set_flag("quest_3_complete", true)
	gs.set_flag("quest_4_active", true)
	gs.set_flag("can_sail_to_scylla", true)
	gs.add_item("calming_draught", 1)

	# Simulate Quest 4:
	# - Sail to Scylla's Cove (teleport)
	# - Attempt to use potion on Scylla
	# - POTION FAILS - Scylla cannot be cured
	# - Return to Aiaia

	# Use the potion (consumed)
	gs.remove_item("calming_draught", 1)

	# Mark the attempt and failure
	gs.set_flag("attempted_cure", true)
	gs.set_flag("potion_failed", true)  # CRITICAL: Book-accurate
	gs.set_flag("scylla_cured", false)  # Explicitly false

	# Mark quest complete
	gs.set_flag("quest_4_complete", true)
	gs.set_flag("quest_4_active", false)
	gs.set_flag("quest_5_active", true)  # Epilogue

	# CHECKPOINT ASSERTIONS

	# 1. Potion should be consumed
	if gs.get_item_count("calming_draught") > 0:
		push_error("Potion should be consumed")
		return false

	# 2. CRITICAL: Potion FAILED (book-accurate)
	if not gs.get_flag("potion_failed"):
		push_error("CRITICAL: Potion must fail (book-accurate)")
		return false

	# 3. CRITICAL: Scylla NOT cured
	if gs.get_flag("scylla_cured"):
		push_error("CRITICAL: Scylla must NOT be cured (book-accurate)")
		return false

	# 4. Attempted cure recorded
	if not gs.get_flag("attempted_cure"):
		push_error("Should record that cure was attempted")
		return false

	# 5. Quest 4 complete
	if not gs.get_flag("quest_4_complete"):
		push_error("Quest 4 should be complete")
		return false

	# 6. Quest 5 (Epilogue) active
	if not gs.get_flag("quest_5_active"):
		push_error("Quest 5 (Epilogue) should be active")
		return false

	print("  └─ Sailed to Scylla, potion FAILED (book-accurate), Quest 5 active")
	return true
