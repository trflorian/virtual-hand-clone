extends RigidBody3D

class_name Bullet

const BULLET_SPEED := 60.0

var direction: Vector3

func _physics_process(_delta: float) -> void:
	linear_velocity = direction * BULLET_SPEED
