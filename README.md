# Virtual Hand Clone

[![Godot 4.5](https://img.shields.io/badge/Godot-4.5-478CBF?style=flat&logo=godot%20engine&logoColor=white)](https://godotengine.org)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License MIT](https://img.shields.io/github/license/trflorian/virtual-hand-clone)](https://opensource.org/licenses/MIT)

In this project I created a digital 3D clone of my hands with a single webcam. 
To track the hands, I use [mediapipe](https://mediapipe.readthedocs.io/en/latest/solutions/hands.html) with OpenCV and Python.
The identified hand landmark coordinates are then packaged and sent via UDP to [Godot](https://godotengine.org/), where the virtual hands are then visualized.

![godot_animation](https://github.com/trflorian/virtual-hand-clone/assets/27728267/c638b216-4504-4d40-95d9-c0420a96f819)

## ⚡ Quickstart
1. Clone the repo
2. Open the `python` folder and use `uv sync` to create a virtual environment
3. Run the python script `python hand_detection.py`
4. Open the Godot project in the `godot` folder in the Godot Game Engine.
5. Run the project.

## 🗞️ Tutorial
[Real-Time Hand Tracking in Godot — Creating Virtual 3D Clones of my Hands](https://medium.com/@flip.flo.dev/real-time-hand-tracking-in-godot-creating-virtual-3d-clones-of-my-hands-ecbfb73c2fcf)

## 🏗️ Architecture
![ArchitectureHandClone drawio](https://github.com/trflorian/virtual-hand-clone/assets/27728267/81ce01aa-d37e-46d8-bad4-6c65eae6936e)

## 🖥️ Versions

- Python 3.12
- Godot v4.5

## 🎬 Demos
### Single Hand Tracking
![animation](https://github.com/trflorian/virtual-hand-clone/assets/27728267/b412dbdb-1082-450e-89dc-88f635e2bfd7)
