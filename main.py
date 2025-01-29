import serial
import time
from ultralytics import YOLO
import cv2

# Initialize serial communication with Arduino
arduino = serial.Serial('COM16', 9600, timeout=1)  # Replace COM3 with your port (Linux: '/dev/ttyUSB0')

# Load the YOLO model
model = YOLO('yolo11n.pt')

# Video file path
video_path = "highway.mp4"  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

cv2.namedWindow('Vehicle Detection in Video', cv2.WINDOW_NORMAL)

entry_count = 0
exit_count = 0

line_y = 500
line_start_x = 200
line_end_x = 1000
tracked_objects = {}

# List of vehicle classes (car, motorcycle, bus, truck, etc.)
vehicle_classes = [2, 3, 5, 7]  # Add more class IDs if needed

while True:
    ret, frame = cap.read()
    if not ret:
        print("End of video.")
        break

    results = model.track(frame, persist=True)
    vehicle_boxes = []

    for result in results:
        for box in result.boxes:
            obj_id = box.id
            cls = int(box.cls)

            # Check if the class is one of the vehicle classes (car, motorcycle, bus, truck)
            if obj_id is not None and cls in vehicle_classes:
                vehicle_boxes.append((int(obj_id), box.xyxy[0]))  # Store ID and bounding box

    for obj_id, box in vehicle_boxes:
        x1, y1, x2, y2 = map(int, box)
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if obj_id not in tracked_objects:
            tracked_objects[obj_id] = (cx, cy)
        else:
            prev_cx, prev_cy = tracked_objects[obj_id]

            if prev_cy < line_y and cy >= line_y:  # Crossed from top to bottom (entry)
                exit_count += 1
                print(f"Vehicle {obj_id} entered. Entry count: {exit_count}")
                arduino.write(b'1')  # Turn on entry LED
                time.sleep(0.5)      # Delay to avoid rapid flickering
                arduino.write(b'0')  # Turn off entry LED

            elif prev_cy >= line_y and cy < line_y:  # Crossed from bottom to top (exit)
                entry_count += 1
                print(f"Vehicle {obj_id} exited. Exit count: {entry_count}")
                arduino.write(b'2')  # Turn on exit LED
                time.sleep(0.5)      # Delay to avoid rapid flickering
                arduino.write(b'0')  # Turn off exit LED

            tracked_objects[obj_id] = (cx, cy)

    cv2.line(frame, (line_start_x, line_y), (line_end_x, line_y), (0, 0, 255), 2)
    cv2.putText(frame, f"Entries: {entry_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, f"Exits: {exit_count}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Vehicle Detection in Video', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
