extends RigidBody3D

func _process(_delta: float) -> void:
	# respawn box if below ground
	if abs(global_position.y) > 20 or abs(global_position.x) > 30:
		global_position = Vector3(0, 15, 0)
		linear_velocity = Vector3.ZERO
		angular_velocity = Vector3.ZERO
