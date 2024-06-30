extends Node3D

const PORT: int = 4242

var server: UDPServer

var hands: Array = []

func _ready() -> void:
	server = UDPServer.new()
	server.listen(PORT)

func _parse_hands_from_packet(data: PackedByteArray) -> Array:
	var json_string = data.get_string_from_utf8()
	var json = JSON.new()
	var error = json.parse(json_string)
	if error == OK:
		var data_received = json.data
		if typeof(data_received) == TYPE_ARRAY:
			return data_received
		else:
			print("Unexpected data")
			return []
	else:
		print("JSON Parse Error: %s in %s at line %d" % [json.get_error_message(), json_string, json.get_error_line()])
		return []

func _create_new_hand() -> void:
	var hand_instance := Hand.new()
	add_child(hand_instance)
	hands.append(hand_instance)

func _process(_delta: float) -> void:
	server.poll()
	if server.is_connection_available():
		var peer = server.take_connection()
		var data = peer.get_packet()
		var hands_data = _parse_hands_from_packet(data)
		
		var len_diff = len(hands_data) - len(hands)
		
		if len_diff > 0:
			for i in range(len_diff):
				_create_new_hand()
		
		if len_diff < 0:
			for i in range(-len_diff):
				# TODO: add hand identifier and track same hand
				var last_hand: Hand = hands.pop_back()
				last_hand.queue_free()
		
		for hand_id in hands_data.size():
			hands[hand_id].parse_hand_landmarks_from_data(hands_data[hand_id])
