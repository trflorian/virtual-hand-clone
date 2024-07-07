extends RigidBody3D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if abs(global_position.y) > 20 or abs(global_position.x) > 30:
		global_position = Vector3(0, 15, 0)
		linear_velocity = Vector3.ZERO
		angular_velocity = Vector3.ZERO
