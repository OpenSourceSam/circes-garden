extends CharacterBody2D

@export var speed: float = 100.0

@onready var interaction_zone: Area2D = $InteractionZone
@onready var interaction_label: Label = $InteractionPrompt

var _nearby_interactable: Node = null

func _ready() -> void:
	add_to_group("player")
	interaction_label.hide()

func _physics_process(_delta: float) -> void:
	var input_dir := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	velocity = input_dir * speed
	move_and_slide()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") and _nearby_interactable:
		_nearby_interactable.interact()

func _on_interaction_zone_body_entered(body: Node) -> void:
	if body != self and body.has_method("interact"):
		_nearby_interactable = body
		interaction_label.show()

func _on_interaction_zone_body_exited(body: Node) -> void:
	if body == _nearby_interactable:
		_nearby_interactable = null
		interaction_label.hide()

func _on_interaction_zone_area_entered(area: Area2D) -> void:
	if area.has_method("interact"):
		_nearby_interactable = area
		interaction_label.show()

func _on_interaction_zone_area_exited(area: Area2D) -> void:
	if area == _nearby_interactable:
		_nearby_interactable = null
		interaction_label.hide()
