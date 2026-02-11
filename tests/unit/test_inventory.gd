extends RefCounted
## Unit tests for GameState inventory system

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	var all_passed := true

	all_passed = _test_add_item() and all_passed
	all_passed = _test_remove_item() and all_passed
	all_passed = _test_has_item() and all_passed
	all_passed = _test_get_item_count() and all_passed

	return all_passed

func _test_add_item() -> bool:
	gs.inventory.clear()

	gs.add_item("test_item", 5)

	if gs.inventory.get("test_item", 0) != 5:
		push_error("add_item: Expected 5, got %d" % gs.inventory.get("test_item", 0))
		return false

	# Add more to existing
	gs.add_item("test_item", 3)

	if gs.inventory.get("test_item", 0) != 8:
		push_error("add_item (stack): Expected 8, got %d" % gs.inventory.get("test_item", 0))
		return false

	return true

func _test_remove_item() -> bool:
	gs.inventory.clear()
	gs.add_item("test_item", 10)

	var success: bool = gs.remove_item("test_item", 3)

	if not success:
		push_error("remove_item: Should return true")
		return false

	if gs.inventory.get("test_item", 0) != 7:
		push_error("remove_item: Expected 7, got %d" % gs.inventory.get("test_item", 0))
		return false

	# Remove more than available
	success = gs.remove_item("test_item", 100)
	if success:
		push_error("remove_item: Should return false when insufficient")
		return false

	return true

func _test_has_item() -> bool:
	gs.inventory.clear()
	gs.add_item("test_item", 5)

	if not gs.has_item("test_item", 1):
		push_error("has_item: Should have 1")
		return false

	if not gs.has_item("test_item", 5):
		push_error("has_item: Should have 5")
		return false

	if gs.has_item("test_item", 6):
		push_error("has_item: Should NOT have 6")
		return false

	if gs.has_item("nonexistent"):
		push_error("has_item: Should NOT have nonexistent item")
		return false

	return true

func _test_get_item_count() -> bool:
	gs.inventory.clear()

	if gs.get_item_count("nonexistent") != 0:
		push_error("get_item_count: Nonexistent should be 0")
		return false

	gs.add_item("test_item", 42)

	if gs.get_item_count("test_item") != 42:
		push_error("get_item_count: Expected 42")
		return false

	return true
