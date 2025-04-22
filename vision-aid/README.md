

# 👁️‍🗨️ VisionAid: Navigation Assistant for the Visually Impaired

**VisionAid** is a web-based navigation tool designed to assist visually impaired users using real-time camera-based object detection. It identifies nearby objects, estimates their distance, and delivers audio feedback via a Python backend powered by YOLOv8 and FastAPI.

---

## 🗂 Project Structure

<pre lang="markdown"><code>```
vision-aid/
├── backend/
│   ├── main.py              # FastAPI backend server
│   ├── requirements.txt     # Python dependencies
│   └── utils/
│       ├── detection.py     # YOLOv8 object detection logic
│       └── distance.py      # Distance estimation logic
├── src/
│   ├── input.css            # Tailwind CSS input file
│   └── output.css           # Generated Tailwind CSS
├── index.html               # Frontend interface
├── package.json             # Frontend dependencies
├── tailwind.config.js       # Tailwind configuration
└── README.md                # Project documentation
```</code></pre>


---

## ⚙️ Setup

### ✅ Prerequisites

- [Node.js (v20+)](https://nodejs.org/)
- [Python 3.8+](https://www.python.org/)
- Smartphone with Chrome or Safari for testing

---

## 🎨 Frontend Setup

### 1. Install Dependencies

```bash
cd /path/to/vision-aid
npm install

2. Build Tailwind CSS

npm run build:css



⸻

🧠 Backend Setup

1. Create Virtual Environment

cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install Dependencies

pip install -r requirements.txt

3. Run the Backend

uvicorn main:app --host 0.0.0.0 --port 8000



⸻

🌐 Serve the App

Option 1: Run Local Server (Frontend Testing)

cd /path/to/vision-aid
npm install -g http-server
http-server



⸻

📱 How to Test
	1.	Open http://localhost:8000 on a smartphone (Chrome/Safari).
	2.	Grant camera permissions when prompted.
	3.	Ensure a well-lit environment with common objects (e.g., chair, table) 1–3 meters away.
	4.	Open the browser console (F12 → Console) to view logs.

⸻

📋 Requirements
	•	Google Chrome or Safari (preferably on mobile)
	•	Access via localhost or HTTPS for camera usage
	•	A well-lit environment
	•	Running backend server (uvicorn)

⸻

🛠 Troubleshooting

Issue	Solution
❌ No detections	Check lighting, ensure objects are 1–3m away, verify console logs.
🛑 Backend errors	Ensure uvicorn is running and dependencies are installed.
🔌 WebSocket issues	Confirm backend is reachable at ws://localhost:8000/ws.
🐢 Lag	Adjust FRAME_RATE in index.html (e.g., 1000 ms for 1 FPS).
🐞 Other errors	Share console logs and terminal output with the development team.



⸻

📄 License

This project is licensed under the MIT License.

