# VisionAid: Navigation Assistant for the Visually Impaired

VisionAid turns a phone or laptop camera into a spoken navigation aid. The browser streams frames over a WebSocket to a FastAPI backend running YOLOv8. The backend picks the object nearest the centre of view, estimates its distance with a pinhole-camera model, and the page announces it aloud, for example "chair, 1.4 metres, to your left".

```
camera ─► index.html (getUserMedia, canvas) ──frames over /ws──► FastAPI ─► YOLOv8 ─► closest object
   ▲                                                                                       │
   └──────────── speechSynthesis: "<object>, <distance> m, <direction>" ◄──────── JSON ────┘
```

## Run

```bash
cd vision-aid/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open `http://localhost:8000`, allow camera access, and press start. The first run downloads the YOLOv8 weights automatically; weights are not stored in git.

Phones require HTTPS for camera access. Put the server behind a TLS reverse proxy or an HTTPS tunnel; the page connects to `/ws` on whatever origin served it.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `VISIONAID_MODEL` | `yolov8m.pt` | `yolov8n.pt` for low-power devices |
| `VISIONAID_CONFIDENCE` | `0.6` | Minimum detection confidence |
| `VISIONAID_FOCAL_LENGTH` | `1000` | Camera focal length in pixels; calibrate for accurate distances |

## How distance works

`distance = real_width * focal_length / pixel_width`, using typical widths for the 80 COCO classes YOLOv8 detects (see `OBJECT_WIDTHS` in `backend/main.py`). Accuracy depends on calibrating `VISIONAID_FOCAL_LENGTH` for your camera.

## Tests

```bash
pip install -r backend/requirements-dev.txt
cd backend && pytest -q
```

## Styling

```bash
npm install && npm run build:css    # Tailwind -> src/output.css
```
