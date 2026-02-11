extends Control

@onready var start_button: Button = $CenterContainer/VBoxContainer/StartButton

func _ready() -> void:
	_setup_gradient_background()
	start_button.pressed.connect(_on_start_pressed)
	start_button.grab_focus()
	AudioController.play_music("menu")

func _setup_gradient_background() -> void:
	var bg := $Background
	var gradient := Gradient.new()
	gradient.set_color(0, Color(0.18, 0.15, 0.12))  # warm brown (top)
	gradient.set_color(1, Color(0.08, 0.06, 0.05))   # near-black (bottom)

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
	tex_rect.show_behind_parent = false

	# Replace the ColorRect with gradient TextureRect
	bg.add_sibling(tex_rect)
	move_child(tex_rect, bg.get_index())
	bg.queue_free()

func _on_start_pressed() -> void:
	AudioController.play_sfx("ui_confirm")
	GameState.new_game()
	SceneManager.change_scene("res://game/scenes/prologue.tscn")
