extends Node3D

class_name Bullet

const BULLET_SPEED := 40.0

var direction: Vector3

func _process(delta: float) -> void:
	global_position += direction * delta * BULLET_SPEED
