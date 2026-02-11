extends RefCounted
## Unit tests for GameState quest flags system

var gs: Node

func run(game_state: Node) -> bool:
	gs = game_state
	var all_passed := true

	all_passed = _test_set_flag() and all_passed
	all_passed = _test_get_flag() and all_passed
	all_passed = _test_flag_default() and all_passed

	return all_passed

func _test_set_flag() -> bool:
	gs.quest_flags.clear()

	gs.set_flag("test_flag", true)

	if gs.quest_flags.get("test_flag", false) != true:
		push_error("set_flag: Should be true")
		return false

	gs.set_flag("test_flag", false)

	if gs.quest_flags.get("test_flag", true) != false:
		push_error("set_flag: Should be false after update")
		return false

	return true

func _test_get_flag() -> bool:
	gs.quest_flags.clear()
	gs.quest_flags["existing_flag"] = true

	if gs.get_flag("existing_flag") != true:
		push_error("get_flag: Should return true for existing flag")
		return false

	return true

func _test_flag_default() -> bool:
	gs.quest_flags.clear()

	# Non-existent flags should return false
	if gs.get_flag("nonexistent_flag") != false:
		push_error("get_flag: Should return false for nonexistent flag")
		return false

	return true
