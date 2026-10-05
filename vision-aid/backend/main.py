"""
VisionAid backend: receives camera frames over a WebSocket, runs YOLOv8, and
returns the object closest to the centre of view with an estimated distance and
direction for spoken guidance.
"""
import base64
import binascii
import logging
import os
import time
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from ultralytics import YOLO

from utils.detection import detect_objects
from utils.distance import estimate_distance, get_direction

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("visionaid")

BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR.parent / "index.html"

# Weights are downloaded by ultralytics on first run; nothing large lives in git.
MODEL_NAME = os.getenv("VISIONAID_MODEL", "yolov8m.pt")
CONFIDENCE_THRESHOLD = float(os.getenv("VISIONAID_CONFIDENCE", "0.6"))
FOCAL_LENGTH = float(os.getenv("VISIONAID_FOCAL_LENGTH", "1000"))  # pixels, calibrate per camera
CANVAS_WIDTH, CANVAS_HEIGHT = 640, 480
INFER_WIDTH, INFER_HEIGHT = 320, 240
MIN_PROCESSING_INTERVAL = 0.2  # seconds between inferences per client
MIN_BBOX_AREA = 3000  # in canvas pixels
MAX_FRAME_BYTES = 2 * 1024 * 1024

# Typical real-world widths (metres) for COCO classes YOLOv8 can detect.
OBJECT_WIDTHS = {
    "person": 0.5, "bicycle": 0.6, "car": 1.8, "motorcycle": 0.8, "bus": 2.5, "truck": 2.5,
    "traffic light": 0.3, "fire hydrant": 0.3, "stop sign": 0.75, "bench": 1.5, "dog": 0.6,
    "cat": 0.3, "backpack": 0.3, "umbrella": 1.0, "handbag": 0.35, "suitcase": 0.45,
    "bottle": 0.07, "cup": 0.09, "fork": 0.03, "knife": 0.03, "spoon": 0.04, "bowl": 0.15,
    "chair": 0.5, "couch": 2.0, "potted plant": 0.3, "bed": 1.6, "dining table": 1.2,
    "toilet": 0.4, "tv": 1.0, "laptop": 0.35, "mouse": 0.06, "remote": 0.05,
    "keyboard": 0.45, "cell phone": 0.07, "microwave": 0.5, "oven": 0.6, "sink": 0.6,
    "refrigerator": 0.8, "book": 0.15, "clock": 0.3, "vase": 0.15, "scissors": 0.08,
    "toothbrush": 0.02,
}
DEFAULT_WIDTH = 0.5
DISPLAY_NAMES = {"cell phone": "mobile phone", "tv": "television", "dining table": "table"}

app = FastAPI(title="VisionAid")
model = YOLO(MODEL_NAME)


def decode_frame(message: str):
    """Decode a data-URL JPEG/PNG frame; returns None for anything malformed."""
    if len(message) > MAX_FRAME_BYTES * 4 // 3 + 64 or "," not in message:
        return None
    try:
        raw = base64.b64decode(message.split(",", 1)[1], validate=True)
    except (binascii.Error, ValueError):
        return None
    frame = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    return frame


def closest_object(predictions):
    """Pick the detection nearest the centre of view and describe it."""
    sx, sy = CANVAS_WIDTH / INFER_WIDTH, CANVAS_HEIGHT / INFER_HEIGHT
    cx, cy = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2
    best, best_dist = None, float("inf")
    for pred in predictions:
        x, y, w, h = pred["bbox"]
        x, y, w, h = x * sx, y * sy, w * sx, h * sy
        if w * h < MIN_BBOX_AREA or w <= 0:
            continue
        d = ((x + w / 2 - cx) ** 2 + (y + h / 2 - cy) ** 2) ** 0.5
        if d < best_dist:
            best_dist, best = d, (pred, x, y, w, h)
    if best is None:
        return None
    pred, x, y, w, h = best
    name = pred["class"]
    return {
        "class": DISPLAY_NAMES.get(name, name),
        "confidence": round(pred["confidence"], 2),
        "distance": round(estimate_distance(w, OBJECT_WIDTHS.get(name, DEFAULT_WIDTH), FOCAL_LENGTH), 1),
        "direction": get_direction(x + w / 2, CANVAS_WIDTH),
        "bbox": [int(x), int(y), int(w), int(h)],
    }


@app.get("/")
async def index():
    return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_processed = 0.0
    try:
        while True:
            message = await websocket.receive_text()
            now = time.monotonic()
            if now - last_processed < MIN_PROCESSING_INTERVAL:
                continue
            frame = decode_frame(message)
            if frame is None:
                await websocket.send_json({"predictions": [], "error": "invalid frame"})
                continue
            frame = cv2.resize(frame, (INFER_WIDTH, INFER_HEIGHT))
            found = closest_object(detect_objects(model, frame, CONFIDENCE_THRESHOLD))
            await websocket.send_json({"predictions": [found] if found else []})
            last_processed = now
    except WebSocketDisconnect:
        pass
    except Exception:
        log.exception("WebSocket handler failed")
        await websocket.close(code=1011)
