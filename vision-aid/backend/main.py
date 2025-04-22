from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
import base64
from ultralytics import YOLO
from utils.detection import detect_objects
from utils.distance import estimate_distance, get_direction
import json
import time

app = FastAPI()

# Load YOLOv8 medium model
model = YOLO("yolov8m.pt")

# Known object widths (in meters)
object_widths = {
    "cell phone": 0.07,
    "laptop": 0.35,
    "book": 0.2,
    "playing card": 0.09,
    "bottle": 0.06,
    "cord": 0.05,
    "keyboard": 0.4,
    "person": 0.5,
    "chair": 0.5,
    "table": 1.0,
    "car": 1.8,
    "dog": 0.6,
    "spoon": 0.2,
    "fork": 0.2,
    "knife": 0.2,
    "remote": 0.2,
    "umbrella": 0.1,
    "wallet": 0.1,  

    "bag": 0.3,
    "cup": 0.1,
    "plate": 0.3,
    "glasses": 0.14,
    "watch": 0.2,
    "headphones": 0.15,
    "keys": 0.05,
    "charger": 0.05,
    "sanitizer": 0.15,
    "mouse": 0.1,
    "remote control": 0.2,
    "tissue": 0.1,
    "earphones": 0.1,
    "power bank": 0.1,
    "wallet": 0.1,
    "notebook": 0.3,
    "pencil": 0.2,
    "pen": 0.2,
    "calculator": 0.3,
    "flashlight": 0.2,
    "umbrella": 0.1,
    "sunglasses": 0.14,
    "headset": 0.2,
    "camera": 0.2,
    "tripod": 0.5,
    "speaker": 0.3,
    "microphone": 0.2,
    "cable": 0.05,
    "adapter": 0.05,
    "extension cord": 0.2,
    "power strip": 0.3,

    "notebook": 0.3,
    "folder": 0.3,
    "binder": 0.3,
    "sticky notes": 0.1,
    "paper": 0.1,
    "envelope": 0.2,
    "post-it notes": 0.1,   
    "paperclip": 0.01,
    "stapler": 0.2,
    "rubber band": 0.01,
    "eraser": 0.02,
    "highlighter": 0.2,
    "marker": 0.2,
    "tape": 0.02,
    "scissors": 0.2,
    "calculator": 0.3,
    "glue": 0.1,
    "ruler": 0.3,
    "paintbrush": 0.2,
    "palette": 0.3,
    "canvas": 0.5,
    "watercolor": 0.2,
    "oil paint": 0.2,
    "acrylic paint": 0.2,
    "paint": 0.2,
    "paint tube": 0.2,
    "paint palette": 0.3,
    "paintbrush": 0.2,
    
    "default": 0.5
}

# Class name mapping
class_mapping = {
    "cell phone": "mobile",
    "playing card": "cards",
    "bottle": "sanitizer",
    "cord": "charger",
    "keyboard": "keyboard"
}

# Configuration
FOCAL_LENGTH = 1000  # Calibrated for mobile cameras
CONFIDENCE_THRESHOLD = 0.7
CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
MIN_PROCESSING_INTERVAL = 0.2  # Reduced
MIN_BBOX_AREA = 3000

@app.get("/")
async def get():
    with open("../index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_processed = 0
    try:
        while True:
            data = await websocket.receive_text()
            current_time = time.time()
            if current_time - last_processed < MIN_PROCESSING_INTERVAL:
                continue

            img_data = base64.b64decode(data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            frame = cv2.resize(frame, (320, 240))
            predictions = detect_objects(model, frame, CONFIDENCE_THRESHOLD)

            results = []
            center_x, center_y = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2
            closest_dist = float('inf')
            closest_pred = None

            for pred in predictions:
                x, y, width, height = pred['bbox']
                bbox_area = width * height
                if bbox_area < MIN_BBOX_AREA or pred['confidence'] < CONFIDENCE_THRESHOLD:
                    print(f"Filtered out: {pred['class']}, Confidence: {pred['confidence']}, Area: {bbox_area}")
                    continue

                x *= CANVAS_WIDTH / 320
                y *= CANVAS_HEIGHT / 240
                width *= CANVAS_WIDTH / 320
                height *= CANVAS_HEIGHT / 240

                bbox_center_x = x + width / 2
                bbox_center_y = y + height / 2
                dist = ((bbox_center_x - center_x) ** 2 + (bbox_center_y - center_y) ** 2) ** 0.5

                object_width = object_widths.get(pred['class'], object_widths['default'])
                distance = estimate_distance(width, object_width, FOCAL_LENGTH)
                print(f"Raw prediction: {pred['class']}, Confidence: {pred['confidence']}, Distance to center: {dist}, Estimated distance: {distance:.1f}m")

                if dist < closest_dist:
                    closest_dist = dist
                    closest_pred = pred

            if closest_pred:
                x, y, width, height = closest_pred['bbox']
                x *= CANVAS_WIDTH / 320
                y *= CANVAS_HEIGHT / 240
                width *= CANVAS_WIDTH / 320
                height *= CANVAS_HEIGHT / 240
                object_name = closest_pred['class']
                confidence = closest_pred['confidence']

                display_name = class_mapping.get(object_name, object_name)
                object_width = object_widths.get(object_name, object_widths['default'])
                distance = estimate_distance(width, object_width, FOCAL_LENGTH)
                direction = get_direction(x + width / 2, CANVAS_WIDTH)

                results.append({
                    "class": display_name,
                    "confidence": confidence,
                    "distance": round(distance, 1),
                    "direction": direction,
                    "bbox": [int(x), int(y), int(width), int(height)]
                })

            await websocket.send_json({"predictions": results})
            last_processed = current_time
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()