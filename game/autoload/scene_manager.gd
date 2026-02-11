extends Node
## SceneManager - Handle scene transitions with fade effects

signal transition_started
signal transition_midpoint  # When screen is fully black
signal transition_finished

var _fade_layer: ColorRect = null
var _is_transitioning: bool = false

func _ready() -> void:
	_create_fade_layer()
	print("[SceneManager] Initialized")

func _create_fade_layer() -> void:
	_fade_layer = ColorRect.new()
	_fade_layer.name = "FadeLayer"
	_fade_layer.color = Color(0, 0, 0, 0)
	_fade_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_layer.z_index = 100

	# Make it cover the whole screen
	_fade_layer.set_anchors_preset(Control.PRESET_FULL_RECT)

	# Add to scene tree (will be reparented as needed)
	call_deferred("_add_fade_layer")

func _add_fade_layer() -> void:
	get_tree().root.add_child(_fade_layer)

# ============================================
# SCENE CHANGES
# ============================================

func change_scene(scene_path: String, fade_duration: float = 0.5) -> void:
	if _is_transitioning:
		return

	_is_transitioning = true
	transition_started.emit()

	# Fade out
	await _fade_out(fade_duration)

	transition_midpoint.emit()

	# Change scene
	get_tree().change_scene_to_file(scene_path)

	# Wait a frame for scene to load
	await get_tree().process_frame

	# Fade in
	await _fade_in(fade_duration)

	_is_transitioning = false
	transition_finished.emit()

# ============================================
# TELEPORT (Same scene, different position)
# Used for traveling between map zones
# ============================================

func teleport_player(target_position: Vector2, fade_duration: float = 0.3) -> void:
	if _is_transitioning:
		return

	_is_transitioning = true
	transition_started.emit()

	# Fade out
	await _fade_out(fade_duration)

	transition_midpoint.emit()

	# Find and move player
	var player = get_tree().get_first_node_in_group("player")
	if player:
		player.global_position = target_position

	# Fade in
	await _fade_in(fade_duration)

	_is_transitioning = false
	transition_finished.emit()

# ============================================
# FADE EFFECTS
# ============================================

func _fade_out(duration: float) -> void:
	var tween = create_tween()
	tween.tween_property(_fade_layer, "color:a", 1.0, duration)
	await tween.finished

func _fade_in(duration: float) -> void:
	var tween = create_tween()
	tween.tween_property(_fade_layer, "color:a", 0.0, duration)
	await tween.finished

func fade_out(duration: float = 0.5) -> void:
	await _fade_out(duration)

func fade_in(duration: float = 0.5) -> void:
	await _fade_in(duration)
