extends Node3D

const NUM_LANDMARKS: int = 21
const HAND_SCALE: float = 30.0
const PORT: int = 4242

@export var landmark_sphere: PackedScene
@export var hand_skeleton: Skeleton3D

var landmarks: Array[Node3D] = []
var hand_lines: Array[MeshInstance3D] = []

const hand_lines_mapping = [
	# Thumb
	[0, 1],
	[1, 2],
	[2, 3],
	[3, 4],
	# Index Finger
	[0, 5],
	[5, 6],
	[6, 7],
	[7, 8],
	# Middle Finger
	[5, 9],
	[9, 10],
	[10, 11],
	[11, 12],
	# Ring Finger
	[9, 13],
	[13, 14],
	[14, 15],
	[15, 16],
	# Pinky
	[0, 17],
	[13, 17],
	[17, 18],
	[18, 19],
	[19, 20],
]

var server: UDPServer

func _ready() -> void:
	server = UDPServer.new()
	server.listen(PORT)
	
	for i in range(NUM_LANDMARKS):
		var landmark_instance = landmark_sphere.instantiate()
		add_child(landmark_instance)
		
		landmarks.append(landmark_instance)
	
	for i in hand_lines_mapping.size():
		var instance := MeshInstance3D.new()
		add_child(instance)
		hand_lines.append(instance)

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
			var pos0 = Vector3(hand[0][0], hand[0][1], hand[0][2])
			var pos1 = Vector3(hand[1][0], hand[1][1], hand[1][2])
			
			var scale = (pos1 - pos0).length()
			#scale = max(min(scale, 0.01), 10.0)
			for lm_id in range(NUM_LANDMARKS):
				var hand_coord = hand[lm_id]
				var pos_cam = Vector3(hand_coord[0], hand_coord[1], hand_coord[2]) - Vector3.ONE * 0.5
				var pos_xyz = Vector3(-pos_cam[0], -pos_cam[1], pos_cam[2])
				#pos_xyz.z /= scale
				landmarks[lm_id].global_position = lerp(landmarks[lm_id].global_position, pos_xyz * HAND_SCALE, 0.5)
			
			for i in hand_lines_mapping.size():
				var mapping = hand_lines_mapping[i]
				var p0 = landmarks[mapping[0]].global_position
				var p1 = landmarks[mapping[1]].global_position
				
				Draw3D.edit_line(hand_lines[i], p0, p1)
				
				#print(lm_id, " ", hand_skeleton.get_bone_name(lm_id))
				#var parent_bone_id = hand_skeleton.get_bone_parent(lm_id)
				#if parent_bone_id == -1:
					#hand_skeleton.set_bone_pose_position(lm_id, pos_xyz )
