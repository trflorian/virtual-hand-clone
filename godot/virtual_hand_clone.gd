extends Node3D

const NUM_LANDMARKS: int = 21
const HAND_SCALE: float = 20.0
const PORT: int = 4242

@export var landmark_sphere: PackedScene

var landmarks: Array[Node3D] = []
var server: UDPServer

func _ready() -> void:
	server = UDPServer.new()
	server.listen(PORT)
	
	for i in range(NUM_LANDMARKS):
		var landmark_instance = landmark_sphere.instantiate()
		add_child(landmark_instance)
		
		landmarks.append(landmark_instance)

func _parse_hands_from_packet(data: PackedByteArray):
	var json_string = data.get_string_from_utf8()
	var json = JSON.new()
	var error = json.parse(json_string)
	if error == OK:
		var data_received = json.data
		if typeof(data_received) == TYPE_ARRAY:
			if len(data_received) == 0:
				return null
				
			# extract first hand
			var hand = data_received[0]
			return hand
		else:
			print("Unexpected data")
			return null
	else:
		print("JSON Parse Error: %s in %s at line %d" % [json.get_error_message(), json_string, json.get_error_line()])
		return null
	

func _process(delta: float) -> void:
	server.poll()
	if server.is_connection_available():
		var peer = server.take_connection()
		var data = peer.get_packet()
		var hand = _parse_hands_from_packet(data)
		
		if hand != null:
			for lm_id in range(NUM_LANDMARKS):
				var hand_coord = hand[lm_id]
				var pos_cam = Vector3(hand_coord[0], hand_coord[1], hand_coord[2]) - Vector3.ONE * 0.5
				var pos_xyz = Vector3(-pos_cam[0], -pos_cam[1], pos_cam[2])
				landmarks[lm_id].global_position = lerp(landmarks[lm_id].global_position, pos_xyz * HAND_SCALE, 0.5)
