
A simulated autonomous mobile robot built with Webots and Python.

The robot uses a camera and a pretrained YOLO object detection model to detect a pedestrian, steer toward the person, search when the person is temporarily lost, and stop when the person is sufficiently close.

# Features

- Real-time person detection using YOLO
- Camera-based target tracking
- Differential-drive steering
- Automatic search behavior when the target is lost
- Temporary detection-loss handling
- Approximate distance estimation using bounding-box size
- Automatic stopping near the target

# Technologies

- Python
- Webots
- Ultralytics YOLO
- OpenCV
- NumPy

## System Architecture

Camera
↓
OpenCV / NumPy
↓
YOLO Object Detection
↓
Person Bounding Box
↓
Position and Size Estimation
↓
Differential-Drive Controller
↓
Left and Right Wheel Motors

# How It Works

1. The Webots e-puck camera captures an image.
2. The image is converted into a NumPy array.
3. YOLO detects people in the camera image.
4. The center of the person's bounding box is calculated.
5. The robot compares the person's position with the center of the camera.
6. The left and right wheel speeds are adjusted to steer toward the person.
7. Bounding-box area is used as an approximate distance measurement.
8. If the person becomes large enough in the image, the robot stops.
9. If the person is temporarily lost, the robot waits briefly before entering search mode.

# Running Project
pip install -r requirements.txt

