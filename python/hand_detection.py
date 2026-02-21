import json
import socket
import time
from pathlib import Path
from typing import Literal, Optional, Sequence

import cv2
import mediapipe as mp

mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def extract_hand_type_index(
    hand_landmarks: list,
    handedness: list,
    hand_type: Literal["left", "right"],
) -> int:
    """
    Extract the index of the hand with the specified type from the multi-handedness list

    Args:
        handedness: List of hand classifications for each hand [[Category(index=0, score=0.9739, display_name='Right', category_name='Right')]]
        hand_type: The type of hand to extract the index for

    Returns:
        Index of the hand with the specified type in the multi-handedness list. Returns -1 if the hand type is not found
    """

    hands_best_classes = []
    for hand_classifications in handedness:
        sorted_classifications = sorted(hand_classifications, key=lambda c: c.score)
        hands_best_classes.append(sorted_classifications[0])

    argmax(hand_classifications)

    hands = filter(
        lambda x: x.category_name.lower() == hand_type and x.score > 0.5, handedness
    )
    hands = sorted(hands, key=lambda x: x.score, reverse=True)

    if len(hands) == 0:
        return -1

    return handedness.index(hands[0])


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

    # Create a hand landmarker instance with the video mode:
    model_path = Path(__file__).parent / "hand_landmarker.task"
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.2,
        min_tracking_confidence=0.2,
    )
    with HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            # Get a frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: failed to capture image")
                break
            frame_timestamp_ms = int(time.time() * 1000)

            # Check the frame for hands
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

            hand_candidates = sorted(
                [
                    (i, hd.score, hd.category_name, [(hl.x, hl.y, hl.z) for hl in hls])
                    for i, (hls, hds) in enumerate(zip(results.hand_landmarks, results.handedness))
                    for hd in hds
                ],
                key=lambda x: x[1],
            )

            left_hand = None
            right_hand = None
            classified_hands = set()

            while len(hand_candidates) > 0:
                i, _, category, landmarks = hand_candidates.pop(0)

                if i in classified_hands:
                    continue

                if category == "Left" and left_hand is None:
                    left_hand = landmarks
                    classified_hands.add(i)
                
                if category == "Right" and right_hand is None:
                    right_hand = landmarks
                    classified_hands.add(i)

            hand_coords = {
                "left": left_hand,
                "right": right_hand,
            }

            # Send the hand coordinates to the client
            encoded_coords = json.dumps(hand_coords)
            client_socket.sendto(encoded_coords.encode(), (server_ip, server_port))

            # Draw the hand landmarks on the frame
            if results.hand_landmarks:
                for hand_landmarks in results.hand_landmarks:
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
