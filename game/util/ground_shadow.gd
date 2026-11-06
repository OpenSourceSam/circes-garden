extends Node2D
## A soft oval shadow under a character's feet or an object's base, so Circe, Hermes, the pigs and
## the small props stand on the ground the way the trees and rocks (shadows in their art) already do.

const COLOR := Color(0.05, 0.08, 0.02, 0.32)

var radius := Vector2(11, 4)

## Adds a shadow as the first child of `owner_node` (drawn under its sprite), centred at `feet`.
static func attach(owner_node: Node2D, feet: Vector2, size: Vector2) -> void:
	var shadow = load("res://game/util/ground_shadow.gd").new()
	shadow.name = "GroundShadow"
	shadow.position = feet
	shadow.radius = size
	shadow.show_behind_parent = true      # under the owner's own picture when the owner is a sprite
	owner_node.add_child(shadow)
	owner_node.move_child(shadow, 0)

func _draw() -> void:
	# Two layers, the outer one fainter, for a soft edge without a texture.
	for layer in [[1.0, 0.55], [0.7, 1.0]]:
		var scale_x: float = layer[0]
		var c := COLOR
		c.a *= layer[1]
		draw_set_transform(Vector2.ZERO, 0.0, Vector2(1.0, radius.y / radius.x))
		draw_circle(Vector2.ZERO, radius.x * scale_x, c)
