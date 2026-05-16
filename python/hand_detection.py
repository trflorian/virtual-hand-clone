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

            # One entry per hand; use top handedness (same as drawing). Higher score first.
            left_hand = None
            right_hand = None
            for hls, hds in sorted(
                zip(results.hand_landmarks, results.handedness),
                key=lambda p: p[1][0].score,
                reverse=True,
            ):
                lm = [[round(hl.x, 3), round(hl.y, 3), round(hl.z, 3)] for hl in hls]
                label = hds[0].category_name
                if label == "Left" and left_hand is None:
                    left_hand = lm
                elif label == "Right" and right_hand is None:
                    right_hand = lm
                if left_hand is not None and right_hand is not None:
                    break

            hand_coords = {"left": left_hand, "right": right_hand}

            # Send the hand coordinates to the client
            encoded_coords = json.dumps(hand_coords)

            # print(encoded_coords)

            client_socket.sendto(encoded_coords.encode(), (server_ip, server_port))

            # Draw the hand landmarks on the frame
            if results.hand_landmarks:
                for hand_landmarks, handedness in zip(results.hand_landmarks, results.handedness):
                    mp_drawing.draw_landmarks(
                        frame_annotated,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                        connection_drawing_spec=mp_drawing_styles.get_default_hand_connections_style(),
                    )

                    # calcualte bbox for the hand
                    pts = np.array(
                        [
                            [int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])]
                            for landmark in hand_landmarks
                        ],
                        dtype=np.int32,
                    )
                    bbox_xywh = cv2.boundingRect(pts)

                    # scale bbox outwards by 10% from center
                    perc_inc = 0.1
                    bbox_xywh = (
                        int(bbox_xywh[0] - bbox_xywh[2] * perc_inc),
                        int(bbox_xywh[1] - bbox_xywh[3] * perc_inc),
                        int(bbox_xywh[2] + 2 * bbox_xywh[2] * perc_inc),
                        int(bbox_xywh[3] + 2 * bbox_xywh[3] * perc_inc),
                    )

                    # clamp bbox to be within the frame
                    bbox_xywh = (
                        max(0, bbox_xywh[0]),
                        max(0, bbox_xywh[1]),
                        min(frame.shape[1], bbox_xywh[2]),
                        min(frame.shape[0], bbox_xywh[3]),
                    )

                    cv2.rectangle(frame_annotated, bbox_xywh, (255, 255, 255), 2)

                    # label left/right handedness
                    classification = handedness[0].category_name
                    score = handedness[0].score
                    cv2.putText(
                        frame_annotated,
                        f"{classification}: {score * 100:.0f}%",
                        (bbox_xywh[0], bbox_xywh[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2,
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

            # cv2.imshow("Hand Tracking", cv2.flip(frame_final, 1))
            cv2.imshow("Hand Tracking", frame_final)
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
