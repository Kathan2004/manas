import math
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Avoid loading YOLO weights in unit tests.
fake = types.ModuleType("ultralytics")
fake.YOLO = lambda *_a, **_k: object()
sys.modules["ultralytics"] = fake

import main  # noqa: E402
from utils.distance import estimate_distance, get_direction  # noqa: E402


def test_distance_pinhole():
    assert estimate_distance(100, 0.5, 1000) == 5.0
    assert math.isinf(estimate_distance(0, 0.5, 1000))


def test_direction_thirds():
    assert get_direction(10, 640) == "to your left"
    assert get_direction(320, 640) == "ahead"
    assert get_direction(600, 640) == "to your right"


def test_decode_rejects_garbage():
    assert main.decode_frame("not a data url") is None
    assert main.decode_frame("data:image/jpeg;base64,@@@") is None


def test_closest_object_prefers_centre_and_filters_tiny():
    preds = [
        {"class": "chair", "confidence": 0.9, "bbox": [0, 0, 60, 60]},
        {"class": "person", "confidence": 0.8, "bbox": [130, 90, 60, 60]},
        {"class": "cup", "confidence": 0.95, "bbox": [150, 110, 5, 5]},
    ]
    found = main.closest_object(preds)
    assert found["class"] == "person"
    assert found["direction"] == "ahead"


def test_display_names():
    found = main.closest_object([{"class": "cell phone", "confidence": 0.9, "bbox": [140, 100, 40, 40]}])
    assert found["class"] == "mobile phone"
