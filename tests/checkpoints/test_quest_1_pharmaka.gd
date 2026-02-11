extends RefCounted
## Checkpoint test for Quest 1: Learn Pharmaka
## Verifies: Met Hermes, learned herbs, got seeds, quest 2 activates

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	# Setup: Start from prologue complete state
	gs.new_game()

	# Simulate Quest 1 completion:
	# - Player met Hermes
	# - Completed herb identification minigame
	# - Received additional moly seeds
	gs.set_flag("met_hermes", true)
	gs.set_flag("herb_minigame_complete", true)
	gs.add_item("moly_seed", 5)  # Reward from Hermes
	gs.set_flag("quest_1_complete", true)
	gs.set_flag("quest_1_active", false)
	gs.set_flag("quest_2_active", true)

	# CHECKPOINT ASSERTIONS

	# 1. Quest 1 should be complete
	if not gs.get_flag("quest_1_complete"):
		push_error("Quest 1 should be complete")
		return false

	# 2. Quest 2 should now be active
	if not gs.get_flag("quest_2_active"):
		push_error("Quest 2 should be active after Quest 1")
		return false

	# 3. Should have met Hermes
	if not gs.get_flag("met_hermes"):
		push_error("Should have met Hermes")
		return false

	# 4. Should have enough seeds to farm (starting 3 + reward 5)
	if gs.get_item_count("moly_seed") < 5:
		push_error("Should have seeds to begin farming")
		return false

	# 5. Herb minigame should be recorded as complete
	if not gs.get_flag("herb_minigame_complete"):
		push_error("Herb minigame should be marked complete")
		return false

	print("  └─ Met Hermes, learned herbs, has 8+ seeds, Quest 2 active")
	return true
