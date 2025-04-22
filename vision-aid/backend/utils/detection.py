from ultralytics import YOLO
import cv2
import numpy as np

def detect_objects(model: YOLO, frame: np.ndarray, confidence_threshold: float):
    # Run YOLOv8 inference
    results = model(frame, conf=confidence_threshold, verbose=False)

    predictions = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            width = x2 - x1
            height = y2 - y1
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]

            predictions.append({
                "class": class_name,
                "confidence": confidence,
                "bbox": [x1, y1, width, height]
            })

    return predictions