#!/bin/bash

# Create project directory
mkdir -p vision-aid/src

# Create index.html
cat << 'EOF' > vision-aid/index.html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VisionAid: Navigation for Visually Impaired</title>
  <link href="src/output.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.21.0/dist/tf.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/coco-ssd@2.2.3/dist/coco-ssd.min.js"></script>
</head>
<body class="bg-gray-100 flex flex-col items-center justify-center min-h-screen">
  <div class="text-center p-4">
    <h1 class="text-2xl font-bold mb-4">VisionAid: Navigation Assistant</h1>
    <p class="text-lg mb-4">Grant camera access to detect objects. Use in a well-lit room, 1–3 meters from objects.</p>
    <button id="startBtn" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" onclick="startCamera()">Start Camera</button>
    <video id="video" class="mt-4 hidden" autoplay playsinline></video>
    <canvas id="canvas" class="hidden"></canvas>
    <p id="status" class="text-lg mt-4">Status: Waiting for camera permission...</p>
  </div>

  <script>
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const status = document.getElementById('status');
    let model, ctx;

    // Known object widths (in meters) for distance estimation
    const objectWidths = {
      'chair': 0.5,
      'table': 1.0,
      'person': 0.5,
      'door': 0.8,
      'default': 0.5
    };

    // Configuration
    const FOCAL_LENGTH = 1000;
    const CONFIDENCE_THRESHOLD = 0.7;
    const FRAME_RATE = 500;

    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 640 },
            height: { ideal: 480 }
          }
        });
        video.srcObject = stream;
        video.classList.remove('hidden');
        canvas.classList.remove('hidden');
        canvas.width = 640;
        canvas.height = 480;
        ctx = canvas.getContext('2d');
        status.textContent = 'Status: Camera active, loading model...';
        speak('Camera active, loading model.');
        console.log('Camera initialized:', stream.getVideoTracks()[0].getSettings());
        loadModel();
      } catch (err) {
        status.textContent = 'Error: Failed to access camera. Please grant permission.';
        speak('Error: Failed to access camera. Please grant permission.');
        console.error('Camera error:', err);
      }
    }

    async function loadModel() {
      try {
        model = await cocoSsd.load();
        status.textContent = 'Status: Model loaded, detecting objects...';
        speak('Model loaded, starting object detection.');
        console.log('Model loaded successfully');
        detectObjects();
      } catch (err) {
        status.textContent = 'Error: Failed to load model.';
        speak('Error: Failed to load model.');
        console.error('Model loading error:', err);
      }
    }

    async function detectObjects() {
      if (!model || video.readyState !== 4) {
        console.warn('Model or video not ready, retrying...');
        setTimeout(detectObjects, FRAME_RATE);
        return;
      }

      try {
        const predictions = await model.detect(video);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        console.log('Predictions:', predictions);

        let detected = false;
        predictions.forEach(prediction => {
          const [x, y, width, height] = prediction.bbox;
          const objectName = prediction.class;
          const confidence = prediction.score;

          if (confidence > CONFIDENCE_THRESHOLD) {
            detected = true;
            ctx.beginPath();
            ctx.rect(x, y, width, height);
            ctx.lineWidth = 2;
            ctx.strokeStyle = 'red';
            ctx.stroke();
            ctx.fillStyle = 'red';
            ctx.fillText(`${objectName} (${(confidence * 100).toFixed(1)}%)`, x, y - 10);

            const objectWidth = objectWidths[objectName] || objectWidths['default'];
            const distance = estimateDistance(width, objectWidth);
            const direction = getDirection(x + width / 2, canvas.width);

            const message = `${objectName} detected, ${distance.toFixed(1)} meters ${direction}.`;
            speak(message);
            console.log(`Detected: ${message}, Confidence: ${confidence}, BBox: [${x}, ${y}, ${width}, ${height}]`);
          }
        });

        if (!detected) {
          status.textContent = 'Status: No objects detected. Try moving closer or improving lighting.';
          console.log('No objects detected above threshold');
        } else {
          status.textContent = 'Status: Detecting objects...';
        }
      } catch (err) {
        console.error('Detection error:', err);
        status.textContent = 'Status: Error during detection.';
        speak('Error during object detection.');
      }

      setTimeout(detectObjects, FRAME_RATE);
    }

    function estimateDistance(pixelWidth, realWidth) {
      return (realWidth * FOCAL_LENGTH) / pixelWidth;
    }

    function getDirection(objectCenter, canvasWidth) {
      const third = canvasWidth / 3;
      if (objectCenter < third) return 'to your left';
      if (objectCenter > 2 * third) return 'to your right';
      return 'ahead';
    }

    function speak(text) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.2;
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    }

    document.getElementById('startBtn').focus();
  </script>
</body>
</html>
EOF

# Create src/input.css
cat << 'EOF' > vision-aid/src/input.css
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# Create src/output.css (placeholder)
cat << 'EOF' > vision-aid/src/output.css
/* This file will be overwritten by 'npm run build:css' */
EOF

# Create tailwind.config.js
cat << 'EOF' > vision-aid/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html"],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# Create package.json
cat << 'EOF' > vision-aid/package.json
{
  "name": "vision-aid",
  "version": "1.0.0",
  "description": "Navigation assistant for visually impaired using object detection",
  "scripts": {
    "build:css": "tailwindcss -i ./src/input.css -o ./src/output.css --minify",
    "watch:css": "tailwindcss -i ./src/input.css -o ./src/output.css --watch"
  },
  "dependencies": {
    "tailwindcss": "^3.4.10"
  }
}
EOF

# Create README.md
cat << 'EOF' > vision-aid/README.md
# VisionAid: Navigation Assistant for Visually Impaired

A web app that uses camera-based object detection to assist visually impaired users in navigating their environment. It detects objects, estimates distances, and provides audio feedback.

## Setup

1. **Install Node.js**: Download and install from [nodejs.org](https://nodejs.org).
2. **Extract the Project**: Unzip the `vision-aid.zip` file.
3. **Install Dependencies**:
   - Open a terminal in the `vision-aid` folder.
   - Run: `npm install`
4. **Build Tailwind CSS**:
   - Run: `npm run build:css`
   - This generates `src/output.css`.
5. **Serve the App**:
   - Install a local server: `npm install -g http-server`
   - Run: `http-server`
   - Open the displayed URL (e.g., `http://127.0.0.1:8080`) in Chrome or Safari.
6. **Test**:
   - Grant camera permission.
   - Test in a well-lit room with objects (e.g., chair, table) 1–3 meters away.
   - Check the browser console (F12 > Console) for detection logs.

## Requirements
- Chrome or Safari browser (smartphone recommended).
- HTTPS or localhost for camera access.
- Well-lit environment for accurate object detection.

## Troubleshooting
- **No detections**: Ensure good lighting, hold camera 1–3 meters from objects, and check console logs.
- **Lag**: Increase `FRAME_RATE` in `index.html` (e.g., to 1000 for 1 FPS).
- **Errors**: Share console logs with the developer.

## License
MIT License
EOF

# Create zip file
zip -r vision-aid.zip vision-aid

# Clean up
rm -rf vision-aid

echo "Created vision-aid.zip"
EOF