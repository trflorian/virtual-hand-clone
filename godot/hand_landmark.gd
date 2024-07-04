extends Area3D

class_name HandLandmark

enum LandmarkType {
	TIP, OTHER
}

enum Finger {
	ROOT, THUMB, INDEX, MIDDLE, RING, PINKY
}

const FINGER_TIPS = [
	4, 8, 12, 16, 20
]

@export var sphere: MeshInstance3D

var landmark_id: int
var finger: Finger
var type: LandmarkType

var _material: Material
var _touching_tips: int = 0

func _ready() -> void:
	_material = StandardMaterial3D.new()
	sphere.set_surface_override_material(0, _material)
	area_entered.connect(_on_area_entered)
	area_exited.connect(_on_area_exited)

func _process(_delta: float) -> void:
	_material.albedo_color = Color.RED if _touching_tips > 0 else Color.WHITE

func is_interaction(lm1: HandLandmark, lm2: HandLandmark) -> bool:
	if lm1.type != LandmarkType.TIP or lm2.type != LandmarkType.TIP:
		return false
	
	return lm1.finger == Finger.THUMB or lm2.finger == Finger.THUMB

func from_landmark_id(id: int) -> void:
	landmark_id = id
	type = LandmarkType.TIP if id in FINGER_TIPS else LandmarkType.OTHER
	
	if id == 0:
		finger = Finger.ROOT
	elif id <= 4:
		finger = Finger.THUMB
	elif id <= 8:
		finger = Finger.INDEX
	elif id <= 12:
		finger = Finger.MIDDLE
	elif id <= 16:
		finger = Finger.RING
	else:
		finger = Finger.PINKY

func _on_area_entered(area: Area3D) -> void:
	var other_landmark = area as HandLandmark
	if is_interaction(self, other_landmark):
		_touching_tips += 1
	
func _on_area_exited(area: Area3D) -> void:
	var other_landmark = area as HandLandmark
	if is_interaction(self, other_landmark):
		_touching_tips -= 1
