import json
import socket

import numpy as np
import cv2

import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles

def extract_hand_type_index(multi_handedness, hand_type: str) -> int:
    hand_classification = [
        hand.classification[0] for hand in multi_handedness
    ]

    hands = filter(lambda x: x.label.lower() == hand_type and x.score > 0.0, hand_classification)
    hands = sorted(hands, key=lambda x: x.score, reverse=True)

    if len(hands) == 0:
        return -1

    return hand_classification.index(hands[0])

def run_hand_tracking_server(
    server_ip: str,
    server_port: int,
):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
        model_complexity=0,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as hands:

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("Error: failed to capture image")
                break

            # Check the frame for hands
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            hand_coords = {
                "left": None,
                "right": None,
            }

            if results.multi_hand_landmarks:
                for hand_type in ["left", "right"]:
                    hand_idx = extract_hand_type_index(results.multi_handedness, hand_type)

                    if hand_idx == -1:
                        continue

                    hand_lms = results.multi_hand_landmarks[hand_idx]

                    hand_coords[hand_type] = [
                        [landmark.x, landmark.y, landmark.z]
                        for landmark in hand_lms.landmark
                    ]

                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=hand_lms,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
                    )

            # Send the hand coordinates to the client
            encoded_coords = json.dumps(hand_coords)
            client_socket.sendto(encoded_coords.encode(), (server_ip, server_port))

            cv2.imshow("Hand Tracking", cv2.flip(frame, 1))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()

    cap.release()


if __name__ == "__main__":
    run_hand_tracking_server(
        server_ip="127.0.0.1",
        server_port=4242,
    )
