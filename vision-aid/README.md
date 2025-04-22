VisionAid: Navigation Assistant for Visually Impaired
A web app that uses camera-based object detection to assist visually impaired users in navigating their environment. It detects objects, estimates distances, and provides audio feedback using a Python backend with YOLOv8.
Project Structure
vision-aid/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt     # Python dependencies
│   └── utils/
│       ├── detection.py     # YOLOv8 detection
│       └── distance.py      # Distance estimation
├── src/
│   ├── input.css           # Tailwind CSS input
│   └── output.css          # Generated Tailwind CSS
├── index.html              # Frontend
├── package.json            # Frontend dependencies
├── tailwind.config.js      # Tailwind config
└── README.md               # This file

Setup
Prerequisites

Node.js: Install from nodejs.org (v20 recommended).
Python: Install Python 3.8+ from python.org.
Smartphone: Chrome/Safari for testing.

Frontend Setup

Install Dependencies:

Navigate to the project folder:
cd /path/to/vision-aid


Run:
npm install




Build Tailwind CSS:

Run:
npm run build:css


This generates src/output.css.




Backend Setup

Create Virtual Environment:

Navigate to the backend folder:
cd backend


Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate




Install Dependencies:

Run:
pip install -r requirements.txt




Run the Backend:

Start the FastAPI server:
uvicorn main:app --host 0.0.0.0 --port 8000


Keep this terminal running.




Serve the App

Start a Local Server:

In a new terminal, navigate to vision-aid:
cd /path/to/vision-aid


Install and run http-server:
npm install -g http-server
http-server


Note: The backend serves index.html at http://localhost:8000, so you may not need http-server unless testing frontend separately.



Test the App:

Open http://localhost:8000 in Chrome/Safari on a smartphone.
Grant camera permission.
Test in a well-lit room with objects (e.g., chair, table) 1–3 meters away.
Check the browser console (F12 > Console) for detection logs.



Requirements

Chrome or Safari (smartphone recommended).
Localhost or HTTPS for camera access.
Well-lit environment for accurate detection.
Backend server running (uvicorn).

Troubleshooting

No Detections: Ensure good lighting, hold camera 1–3 meters from objects, and check console logs.
Backend Errors: Verify uvicorn is running and dependencies are installed. Check terminal for errors.
WebSocket Issues: Ensure the backend is at ws://localhost:8000/ws. Check firewall settings.
Lag: Adjust FRAME_RATE in index.html (e.g., to 1000 for 1 FPS).
Errors: Share console logs and backend terminal output with the developer.

License
MIT License
