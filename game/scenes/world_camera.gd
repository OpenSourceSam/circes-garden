extends Camera2D
## Follows Circe (world.gd parents it to her). In the cove it looks north, so the cliff and
## Scylla's heads fill the screen while Circe stands low on it, clear of the dialogue box.
## Shakes (SceneManager.shake_camera) add on top of that framing.

const COVE_TOP := 1984.0
## How far above Circe the camera centres in the cove, in world pixels.
const COVE_LOOK_NORTH := 150.0

var _shake_left: float = 0.0
var _shake_duration: float = 0.0
var _shake_strength: float = 0.0

## A shake that fades out over `duration`. A weaker shake does not cut a stronger one short.
func shake(duration: float, strength: float) -> void:
	var current := _current_shake_amount()
	if strength < current:
		return
	_shake_duration = maxf(duration, 0.01)
	_shake_left = duration
	_shake_strength = strength

func _current_shake_amount() -> float:
	if _shake_left <= 0.0:
		return 0.0
	return _shake_strength * (_shake_left / _shake_duration)

func _process(delta: float) -> void:
	var target := get_parent() as Node2D
	var look := Vector2.ZERO
	if target and target.global_position.y > COVE_TOP:
		look.y = -COVE_LOOK_NORTH
	# Up and down only: the map is exactly as wide as the screen, so a sideways shake would
	# show the empty edge past the tiles.
	var jitter := Vector2.ZERO
	if _shake_left > 0.0:
		jitter.y = roundf(randf_range(-1.0, 1.0) * _current_shake_amount())
		_shake_left -= delta
	offset = look + jitter
