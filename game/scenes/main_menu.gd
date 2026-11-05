extends Control
## Title screen: the garden painting, the title and its line, golden motes drifting up through
## the light, and Start, which begins a new game with the prologue.

const StoryText := preload("res://game/data/story_text.gd")
const TextureLoaderUtil := preload("res://game/util/texture_loader.gd")
const UiStyle := preload("res://game/ui/ui_style.gd")
const PAINTING_PATH := "res://assets/image_pipeline/generated/raw/cutscenes/prologue/prologue_07.png"
const MOTE_PATH := "res://assets/image_pipeline/generated/raw/sprites/ui/particle_soft.png"
const CREAM := Color(1.0, 0.97, 0.9)
const INK := Color(0.1, 0.06, 0.04, 0.9)

@onready var title_label: Label = $CenterContainer/VBoxContainer/TitleLabel
@onready var start_button: Button = $CenterContainer/VBoxContainer/StartButton

func _ready() -> void:
	_build_background()
	_place_title_block()
	title_label.text = StoryText.MENU["title"]
	_style_title()
	_add_subtitle()
	_style_button()
	_add_motes()
	_add_credit()
	start_button.pressed.connect(_on_start_pressed)
	start_button.grab_focus()
	AudioController.play_music("menu")
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 0.9)

func _build_background() -> void:
	var bg := $Background
	var painting := TextureRect.new()
	painting.name = "Painting"
	painting.texture = TextureLoaderUtil.load_texture(PAINTING_PATH)
	painting.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	painting.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	painting.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.add_sibling(painting)
	move_child(painting, bg.get_index())
	# Darken the lower half so the title reads over the flowers.
	var veil := TextureRect.new()
	veil.name = "Veil"
	var gradient := Gradient.new()
	# Set offsets and colours together: add_point() would shift the indices of set_color().
	gradient.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
	gradient.colors = PackedColorArray([Color(0.08, 0.05, 0.03, 0.0), Color(0.08, 0.05, 0.03, 0.05), Color(0.08, 0.05, 0.03, 0.9)])
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0.5, 0.0)
	texture.fill_to = Vector2(0.5, 1.0)
	texture.width = 2
	texture.height = 128
	veil.texture = texture
	veil.stretch_mode = TextureRect.STRETCH_SCALE
	veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	painting.add_sibling(veil)
	bg.queue_free()

## The title block sits in the lower third, under Circe, not over her face.
func _place_title_block() -> void:
	var center := $CenterContainer
	center.anchor_top = 0.6
	center.offset_top = 0
	$CenterContainer/VBoxContainer.add_theme_constant_override("separation", 18)

func _style_title() -> void:
	title_label.add_theme_font_override("font", UiStyle.TITLE_FONT)
	title_label.add_theme_font_size_override("font_size", 80)
	title_label.add_theme_color_override("font_color", CREAM)
	title_label.add_theme_color_override("font_outline_color", INK)
	title_label.add_theme_constant_override("outline_size", 14)
	title_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.55))
	title_label.add_theme_constant_override("shadow_offset_y", 5)

func _add_subtitle() -> void:
	var subtitle := Label.new()
	subtitle.name = "SubtitleLabel"
	subtitle.text = StoryText.MENU["subtitle"]
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 26)
	subtitle.add_theme_color_override("font_color", UiStyle.GOLD_TEXT)
	subtitle.add_theme_color_override("font_outline_color", INK)
	subtitle.add_theme_constant_override("outline_size", 8)
	title_label.add_sibling(subtitle)
	# A little air between the line and the button.
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 26)
	subtitle.add_sibling(spacer)

func _style_button() -> void:
	start_button.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	start_button.custom_minimum_size = Vector2(300, 64)
	start_button.add_theme_font_size_override("font_size", 28)
	start_button.add_theme_color_override("font_color", CREAM)
	start_button.add_theme_color_override("font_hover_color", UiStyle.GOLD_TEXT)
	start_button.add_theme_color_override("font_focus_color", UiStyle.GOLD_TEXT)
	start_button.add_theme_color_override("font_pressed_color", UiStyle.GOLD_TEXT)
	var normal := UiStyle.panel(28, 10, 2)
	var hover := UiStyle.panel(28, 10, 3)
	hover.bg_color = Color(0.2, 0.14, 0.08, 0.95)
	start_button.add_theme_stylebox_override("normal", normal)
	start_button.add_theme_stylebox_override("hover", hover)
	start_button.add_theme_stylebox_override("focus", hover)
	start_button.add_theme_stylebox_override("pressed", hover)
	# A slow breath on the button so the eye finds it.
	var tween := create_tween().set_loops()
	tween.tween_property(start_button, "modulate", Color(1.08, 1.04, 0.95), 1.4).set_trans(Tween.TRANS_SINE)
	tween.tween_property(start_button, "modulate", Color(1, 1, 1), 1.4).set_trans(Tween.TRANS_SINE)

## Golden motes rising slowly through the sunbeams of the painting.
func _add_motes() -> void:
	var motes := CPUParticles2D.new()
	motes.name = "Motes"
	motes.texture = TextureLoaderUtil.load_texture(MOTE_PATH)
	motes.amount = 46
	motes.lifetime = 9.0
	motes.preprocess = 9.0
	motes.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	var size := get_viewport_rect().size
	motes.position = Vector2(size.x / 2.0, size.y * 0.75)
	motes.emission_rect_extents = Vector2(size.x / 2.0, size.y * 0.3)
	motes.direction = Vector2(0, -1)
	motes.spread = 25.0
	motes.gravity = Vector2(0, -4)
	motes.initial_velocity_min = 6.0
	motes.initial_velocity_max = 18.0
	motes.scale_amount_min = 0.15
	motes.scale_amount_max = 0.45
	var ramp := Gradient.new()
	ramp.offsets = PackedFloat32Array([0.0, 0.25, 1.0])
	ramp.colors = PackedColorArray([Color(1.0, 0.9, 0.6, 0.0), Color(1.0, 0.9, 0.6, 0.7), Color(1.0, 0.9, 0.6, 0.0)])
	motes.color_ramp = ramp
	add_child(motes)
	move_child(motes, $CenterContainer.get_index())

func _add_credit() -> void:
	var credit := Label.new()
	credit.name = "Credit"
	credit.text = "Made by Sam Cloutier with Claude Code"
	credit.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	credit.add_theme_font_size_override("font_size", 18)
	credit.add_theme_color_override("font_color", Color(CREAM, 0.7))
	credit.add_theme_color_override("font_outline_color", INK)
	credit.add_theme_constant_override("outline_size", 6)
	credit.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	credit.offset_left = -300
	credit.offset_right = 300
	credit.offset_top = -48
	credit.offset_bottom = -20
	add_child(credit)

func _on_start_pressed() -> void:
	AudioController.play_sfx("ui_confirm")
	GameState.new_game()
	SceneManager.change_scene("res://game/scenes/prologue.tscn")
