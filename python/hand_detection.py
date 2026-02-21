import json
import socket
import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


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

    # fade in/out landmarks for video
    show_landmarks = True
    alpha = 1.0

    with HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            # Get a frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: failed to capture image")
                break
            frame_annotated = frame.copy()
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
                        frame_annotated,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
                    )
            
            if show_landmarks and alpha < 1.0:
                alpha += 0.05
            elif not show_landmarks and alpha > 0.0:
                alpha -= 0.05
            
            alpha = np.clip(alpha, 0.0, 1.0)
            
            frame = frame.astype(np.float32)
            frame_annotated = frame_annotated.astype(np.float32)
            frame_final = alpha * frame_annotated + (1 - alpha) * frame
            frame_final = frame_final.astype(np.uint8)

            cv2.imshow("Hand Tracking", cv2.flip(frame_final, 1))
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                show_landmarks = not show_landmarks

    cv2.destroyAllWindows()

    cap.release()


if __name__ == "__main__":
    run_hand_tracking_server(
        server_ip="127.0.0.1",
        server_port=4242,
    )
