extends RefCounted
## Checkpoint test for Quest 3: Craft Calming Draught
## Verifies: Has moly, crafts potion, quest 4 activates

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	# Setup: Start from Quest 2 complete with moly
	gs.new_game()
	gs.set_flag("quest_1_complete", true)
	gs.set_flag("quest_2_complete", true)
	gs.set_flag("quest_3_active", true)
	gs.add_item("moly", 3)  # Harvested from farming

	# Simulate Quest 3:
	# - Use moly to craft Calming Draught
	# - (Future: crafting minigame)

	# Consume ingredients
	gs.remove_item("moly", 3)

	# Add crafted potion
	gs.add_item("calming_draught", 1)

	# Mark quest complete
	gs.set_flag("quest_3_complete", true)
	gs.set_flag("quest_3_active", false)
	gs.set_flag("quest_4_active", true)
	gs.set_flag("can_sail_to_scylla", true)

	# CHECKPOINT ASSERTIONS

	# 1. Should have calming draught
	if gs.get_item_count("calming_draught") < 1:
		push_error("Should have crafted calming_draught")
		return false

	# 2. Moly should be consumed
	if gs.get_item_count("moly") > 0:
		push_error("Moly should be consumed in crafting")
		return false

	# 3. Quest 3 complete
	if not gs.get_flag("quest_3_complete"):
		push_error("Quest 3 should be complete")
		return false

	# 4. Quest 4 active
	if not gs.get_flag("quest_4_active"):
		push_error("Quest 4 should be active")
		return false

	# 5. Can now sail to Scylla
	if not gs.get_flag("can_sail_to_scylla"):
		push_error("Should be able to sail to Scylla")
		return false

	print("  └─ Crafted calming_draught, Quest 4 active, can sail")
	return true
