extends Control

@onready var title_label: Label = $CenterContainer/VBoxContainer/TitleLabel
@onready var body_label: Label = $CenterContainer/VBoxContainer/BodyLabel
@onready var prompt_label: Label = $CenterContainer/VBoxContainer/PromptLabel

func _ready() -> void:
	_setup_background_gradient()
	title_label.text = "Circe's Garden"
	body_label.text = "The potion failed.\nScylla remained unchanged.\n\nCirce returned to Aiaia and found peace in what remained."
	prompt_label.text = "Press A / E to return to menu"
	var audio_controller := _audio_controller()
	if audio_controller and audio_controller.has_method("play_music"):
		audio_controller.play_music("epilogue")

func _setup_background_gradient() -> void:
	var gradient := Gradient.new()
	gradient.set_color(0, Color(0.08, 0.1, 0.15))
	gradient.set_color(1, Color(0.02, 0.03, 0.05))

	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0.5, 0.0)
	texture.fill_to = Vector2(0.5, 1.0)
	texture.width = 2
	texture.height = 64

	var tex_rect := TextureRect.new()
	tex_rect.texture = texture
	tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
	tex_rect.set_anchors_preset(Control.PRESET_FULL_RECT)

	var bg := $Background
	bg.add_sibling(tex_rect)
	move_child(tex_rect, bg.get_index())
	bg.queue_free()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") or event.is_action_pressed("ui_accept"):
		var audio_controller := _audio_controller()
		if audio_controller and audio_controller.has_method("play_sfx"):
			audio_controller.play_sfx("ui_confirm")

		var scene_manager := _scene_manager()
		if scene_manager and scene_manager.has_method("change_scene"):
			scene_manager.change_scene("res://game/scenes/main_menu.tscn")
		get_viewport().set_input_as_handled()

func _audio_controller() -> Node:
	return get_tree().root.get_node_or_null("AudioController")

func _scene_manager() -> Node:
	return get_tree().root.get_node_or_null("SceneManager")
