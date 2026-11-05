extends Node
## Scene changes and in-scene teleports behind a fade to black, the night fade used when
## Circe sleeps, and the camera shake for Scylla's scream.

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

	_fade_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	# The root is still being built while autoloads run _ready, so add the layer a frame later.
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
	await _fade_out(fade_duration)
	get_tree().change_scene_to_file(scene_path)
	await get_tree().process_frame
	await _fade_in(fade_duration)

	_is_transitioning = false
	transition_finished.emit()

# ============================================
# TELEPORT (same scene, used by the boats)
# ============================================

func teleport_player(target_position: Vector2, fade_duration: float = 0.3) -> void:
	if _is_transitioning:
		return

	_is_transitioning = true
	await _fade_out(fade_duration)
	var player := get_tree().get_first_node_in_group("player") as Node2D
	if player:
		player.global_position = target_position
		print("[Scene] teleported player to %s" % target_position)
	await _fade_in(fade_duration)

	_is_transitioning = false
	transition_finished.emit()

# ============================================
# FADE EFFECTS
# ============================================

func _fade_out(duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_layer, "color:a", 1.0, duration)
	await tween.finished

func _fade_in(duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_layer, "color:a", 0.0, duration)
	await tween.finished

# ============================================
# NIGHT TRANSITION (sleeping) AND CAMERA SHAKE
# ============================================

func night_transition(day_number: int) -> void:
	# Fade to a starry night, show the new day, fade back. Callers do not await this.
	var layer := CanvasLayer.new()
	layer.layer = 90
	get_tree().root.add_child(layer)
	var sky := ColorRect.new()
	sky.color = Color(0.03, 0.04, 0.12, 0.0)
	sky.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sky.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(sky)
	var rng := RandomNumberGenerator.new()
	rng.seed = day_number * 7919
	var stars: Array[ColorRect] = []
	var view := get_viewport().get_visible_rect().size
	for i in 36:
		var star := ColorRect.new()
		star.color = Color(1, 1, 0.9, 0.0)
		star.size = Vector2(2, 2) if i % 3 else Vector2(3, 3)
		star.position = Vector2(rng.randf() * view.x, rng.randf() * view.y * 0.7)
		star.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.add_child(star)
		stars.append(star)
	var banner := Label.new()
	banner.text = "Day %d" % day_number
	banner.add_theme_font_override("font", preload("res://assets/fonts/title.tres"))
	banner.add_theme_font_size_override("font_size", 48)
	banner.add_theme_color_override("font_color", Color(0.95, 0.9, 0.75, 0.0))
	banner.set_anchors_preset(Control.PRESET_CENTER)
	banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	banner.offset_left = -120
	banner.offset_right = 120
	banner.offset_top = -30
	banner.offset_bottom = 30
	layer.add_child(banner)

	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(sky, "color:a", 0.92, 0.6)
	for star in stars:
		tween.tween_property(star, "color:a", 0.9, 0.9).set_delay(0.2)
	tween.tween_property(banner, "theme_override_colors/font_color:a", 1.0, 0.6).set_delay(0.5)
	await tween.finished
	await get_tree().create_timer(0.9).timeout
	var out := create_tween()
	out.set_parallel(true)
	out.tween_property(sky, "color:a", 0.0, 0.7)
	for star in stars:
		out.tween_property(star, "color:a", 0.0, 0.4)
	out.tween_property(banner, "theme_override_colors/font_color:a", 0.0, 0.5)
	await out.finished
	layer.queue_free()

func shake_camera(duration: float = 0.5, strength: float = 6.0) -> void:
	var camera := get_viewport().get_camera_2d()
	if camera == null:
		return
	var elapsed := 0.0
	while elapsed < duration:
		var t := elapsed / duration
		var amount := strength * (1.0 - t)
		camera.offset = Vector2(randf_range(-amount, amount), randf_range(-amount, amount))
		await get_tree().process_frame
		elapsed += get_process_delta_time()
	camera.offset = Vector2.ZERO
