# Virtual Hand Clone

In this project I created a digital 3D clone of my hands with a single webcam. 
To track the hands, I use [mediapipe](https://mediapipe.readthedocs.io/en/latest/solutions/hands.html) with OpenCV and Python.
The identified hand landmark coordinates are then packaged and sent via UDP to [Godot](https://godotengine.org/), where the virtual hands are then visualized.

![godot_animation](https://github.com/trflorian/virtual-hand-clone/assets/27728267/c638b216-4504-4d40-95d9-c0420a96f819)

## Tutorial
[Real-Time Hand Tracking in Godot — Creating Virtual 3D Clones of my Hands](https://medium.com/@flip.flo.dev/real-time-hand-tracking-in-godot-creating-virtual-3d-clones-of-my-hands-ecbfb73c2fcf)

## Architecture
![ArchitectureHandClone drawio](https://github.com/trflorian/virtual-hand-clone/assets/27728267/81ce01aa-d37e-46d8-bad4-6c65eae6936e)

## Single Hand Tracking
![animation](https://github.com/trflorian/virtual-hand-clone/assets/27728267/b412dbdb-1082-450e-89dc-88f635e2bfd7)
