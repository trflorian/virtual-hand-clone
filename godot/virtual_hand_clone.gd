extends Node3D

const PORT: int = 4242

var server: UDPServer

var hand := Hand.new()

func _ready() -> void:
	server = UDPServer.new()
	server.listen(PORT)
	
	add_child(hand)

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

func _process(delta: float) -> void:
	server.poll()
	if server.is_connection_available():
		var peer = server.take_connection()
		var data = peer.get_packet()
		var hands_data = _parse_hands_from_packet(data)
		
		if len(hands_data) > 0:
			var hand_data = hands_data[0]
			
			hand.parse_hand_landmarks_from_data(hand_data)
