import json
import socket

import numpy as np
import cv2

import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles


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

            hand_coords = []

            # Draw the hand annotations on the image
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=hand_landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
                    )

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_coord_array = [[landmark.x, landmark.y, landmark.z] for landmark in hand_landmarks.landmark]
                    hand_coords.append(hand_coord_array)
            
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
