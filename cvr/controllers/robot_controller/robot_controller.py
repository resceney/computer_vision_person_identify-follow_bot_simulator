from controller import Robot
from ultralytics import YOLO
import numpy as np
import cv2

#robot
robot = Robot()
TIME_STEP = 32


#set camera
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)


#motor
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")

left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))

#yolo ai
model = YOLO("yolo26n.pt")


#speed
BASE_SPEED = 2.5
SEARCH_SPEED = 0.5
TURN_GAIN = 2.0
STOP_AREA_RATIO = 0.08
MAX_SPEED = 5.0

#frames not seen for remembering
lost_frames = 0

#max cap
MAX_LOST_FRAMES = 10

while robot.step(TIME_STEP) != -1:

    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()

    frame = np.frombuffer(image, np.uint8)
    frame = frame.reshape((height, width, 4))
    frame = frame[:, :, :3]
    frame = cv2.resize(frame, (320, 240))

    image_width = 320
    image_height = 240

#image pull
    results = model(
        frame,
        imgsz=320,
        conf=0.20,
        verbose=False
    )

    result = results[0]

    best_person = None
    biggest_area = 0

    for box in result.boxes:

        class_id = int(box.cls[0])
        object_name = model.names[class_id]
        if object_name != "person":
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        box_width = x2 - x1
        box_height = y2 - y1

        area = box_width * box_height
        if area > biggest_area:
            biggest_area = area
            best_person = (x1, y1, x2, y2)


#not found

    if best_person is None:
        lost_frames += 1
        if lost_frames <= MAX_LOST_FRAMES:

            print(
                "PERSON TEMPORARILY LOST",
                lost_frames,
                "/",
                MAX_LOST_FRAMES
            )
            left_motor.setVelocity(0.0)
            right_motor.setVelocity(0.0)

        else:

            print("NO PERSON - SEARCHING")
            left_motor.setVelocity(-SEARCH_SPEED)
            right_motor.setVelocity(SEARCH_SPEED)

        continue


#found person
    lost_frames = 0
    x1, y1, x2, y2 = best_person
    center_x = (x1 + x2) / 2

#calc ratio
    person_area = (x2 - x1) * (y2 - y1)

    image_area = image_width * image_height

    area_ratio = person_area / image_area

#stop
    if area_ratio >= STOP_AREA_RATIO:

        print(
            "PERSON CLOSE - STOP",
            "size:",
            round(area_ratio, 3)
        )

        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)

        continue

#center
    image_center = image_width / 2

    error = (center_x - image_center) / image_center

#moving to the rperson
    turn = TURN_GAIN * error

    left_speed = BASE_SPEED + turn
    right_speed = BASE_SPEED - turn

    left_speed = max(
        -MAX_SPEED,
        min(MAX_SPEED, left_speed)
    )

    right_speed = max(
        -MAX_SPEED,
        min(MAX_SPEED, right_speed)
    )

    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)


    print(
        "PERSON FOUND",
        "center:",
        round(center_x, 1),
        "error:",
        round(error, 2),
        "size:",
        round(area_ratio, 3)
    )