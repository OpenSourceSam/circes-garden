extends SceneTree
## Test runner - executes all tests and reports results

var _tests_passed: int = 0
var _tests_failed: int = 0
var _test_files: Array[String] = []

func _init() -> void:
	print("\n" + "=".repeat(50))
	print("CIRCE'S GARDEN v3 - TEST SUITE")
	print("=".repeat(50) + "\n")

	_collect_tests()
	_run_tests()
	_report_results()

	quit(_tests_failed)  # Exit code = number of failures

func _collect_tests() -> void:
	# Unit tests
	_test_files.append("res://tests/unit/test_inventory.gd")
	_test_files.append("res://tests/unit/test_flags.gd")
	_test_files.append("res://tests/unit/test_farming.gd")

	# Checkpoint tests
	_test_files.append("res://tests/checkpoints/test_quest_0_prologue.gd")
	_test_files.append("res://tests/checkpoints/test_quest_1_pharmaka.gd")
	_test_files.append("res://tests/checkpoints/test_quest_2_farming.gd")
	_test_files.append("res://tests/checkpoints/test_quest_3_crafting.gd")
	_test_files.append("res://tests/checkpoints/test_quest_4_scylla.gd")
	_test_files.append("res://tests/checkpoints/test_quest_5_epilogue.gd")

func _run_tests() -> void:
	# Create a fresh GameState instance for testing
	var gs_script = load("res://game/autoload/game_state.gd")
	var game_state = gs_script.new()

	for test_path in _test_files:
		if not FileAccess.file_exists(test_path):
			print("⏭ SKIP: %s (not found)" % test_path)
			continue

		var test_script = load(test_path)
		if test_script == null:
			print("✗ FAIL: %s (load error)" % test_path)
			_tests_failed += 1
			continue

		var test_instance = test_script.new()
		if test_instance.has_method("run"):
			var result = test_instance.run(game_state)
			if result:
				print("✓ PASS: %s" % test_path)
				_tests_passed += 1
			else:
				print("✗ FAIL: %s" % test_path)
				_tests_failed += 1
		else:
			print("⏭ SKIP: %s (no run method)" % test_path)

func _report_results() -> void:
	print("\n" + "=".repeat(50))
	print("RESULTS: %d passed, %d failed" % [_tests_passed, _tests_failed])
	print("=".repeat(50) + "\n")

	if _tests_failed == 0:
		print("All tests passed!")
	else:
		print("Some tests failed - check output above")
