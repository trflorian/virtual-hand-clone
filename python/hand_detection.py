import json
import socket

from typing import Optional, Sequence, Literal

import cv2

import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles


def extract_hand_type_index(
    multi_handedness: Sequence,
    hand_type: Literal["left", "right"],
) -> int:
    """
    Extract the index of the hand with the specified type from the multi-handedness list

    Args:
        multi_handedness: List of hand classifications for each hand
        hand_type: The type of hand to extract the index for

    Returns:
        Index of the hand with the specified type in the multi-handedness list. Returns -1 if the hand type is not found
    """
    hand_classification = [hand.classification[0] for hand in multi_handedness]

    hands = filter(
        lambda x: x.label.lower() == hand_type and x.score > 0.5, hand_classification
    )
    hands = sorted(hands, key=lambda x: x.score, reverse=True)

    if len(hands) == 0:
        return -1

    return hand_classification.index(hands[0])


def extract_left_right_hand_coords(
    multi_hand_landmarks: Optional[Sequence],
    multi_handedness: Sequence,
) -> dict:
    """
    Extract the coordinates of the left and right hands from the multi-hand landmarks

    Args:
        multi_hand_landmarks: List of landmarks for each hand
        multi_handedness: List of hand classifications for each hand

    Returns:
        Dictionary containing the coordinates of the left and right hands
    """
    hand_coords = {
        "left": None,
        "right": None,
    }

    if multi_hand_landmarks is None:
        return hand_coords
    
    for hand_type in ["left", "right"]:
        hand_idx = extract_hand_type_index(multi_handedness, hand_type)

        if hand_idx == -1:
            continue

        hand_lms = multi_hand_landmarks[hand_idx]

        hand_coords[hand_type] = [
            [landmark.x, landmark.y, landmark.z] for landmark in hand_lms.landmark
        ]

    return hand_coords


def run_hand_tracking_server(
    server_ip: str,
    server_port: int,
) -> None:
    """
    Run the hand tracking which sends the hand coordinates via UDP.
    
    Args:
        server_ip: The IP address of the server
        server_port: The port number of the server
    """
    # Setup the UDP client for sending the hand coordinates
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Open the webcam video feed
    cap = cv2.VideoCapture(0)

    # Create the hand-tracking model
    with mp_hands.Hands(
        model_complexity=0,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as hands:

        while cap.isOpened():
            # Get a frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: failed to capture image")
                break

            # Check the frame for hands. Hnad-tracking requires RGB images, while OpenCV captures in BGR
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            # Extract the hand coordinates from the results into a dictionary:
            # hand_coords = {"left": [[x, y, z], ...], "right": [[x, y, z], ...]}
            hand_coords = extract_left_right_hand_coords(
                results.multi_hand_landmarks,
                results.multi_handedness,
            )

            # Send the hand coordinates to the client
            encoded_coords = json.dumps(hand_coords)
            client_socket.sendto(encoded_coords.encode(), (server_ip, server_port))

            # Draw the hand landmarks on the frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
                    )

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
