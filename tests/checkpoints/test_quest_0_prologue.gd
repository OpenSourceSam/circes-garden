extends RefCounted
## Checkpoint test for Quest 0: Prologue
## Verifies: Game can start, prologue completes, quest 1 activates

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	# Reset state
	gs.inventory.clear()
	gs.quest_flags.clear()
	gs.farm_plots.clear()
	gs.current_day = 1

	# Simulate: new_game() is called
	gs.new_game()

	# CHECKPOINT ASSERTIONS

	# 1. Prologue should be marked complete
	if not gs.get_flag("prologue_complete"):
		push_error("Prologue flag not set after new_game()")
		return false

	# 2. Quest 1 should be active
	if not gs.get_flag("quest_1_active"):
		push_error("Quest 1 should be active after prologue")
		return false

	# 3. Player should have starting items (moly seeds)
	if gs.get_item_count("moly_seed") < 3:
		push_error("Should start with at least 3 moly seeds")
		return false

	# 4. Should be day 1
	if gs.current_day != 1:
		push_error("Should be day 1")
		return false

	print("  └─ Prologue complete, Quest 1 active, has seeds")
	return true
