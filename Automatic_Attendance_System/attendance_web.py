import os
import cv2
from flask import Flask, render_template_string, Response, jsonify
from main import AttendanceEngine

app = Flask(__name__)
engine = AttendanceEngine()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Attendance</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #1e1e2e; color: #cdd6f4; text-align: center; margin: 0; padding: 0; }
        .header { background: #181825; padding: 20px; font-size: 24px; color: #a6e3a1; font-weight: bold; border-bottom: 2px solid #a6e3a1; }
        .container { padding: 40px; }
        .camera-box { border: 4px solid #a6e3a1; border-radius: 12px; overflow: hidden; display: inline-block; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); }
        .btn { padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 16px; border: none; cursor: pointer; text-decoration: none; color: #11111b; margin-top: 20px; }
        .btn-back { background: #89b4fa; }
        .btn-back:hover { background: #b4befe; }
    </style>
</head>
<body>
    <div class="header">🔐 Smart Web Attendance System</div>
    <div class="container">
        <h3>Live Camera Feed</h3>
        <p>Scanning faces for automatic attendance marking...</p>
        <div class="camera-box">
            <img src="/video_feed" width="640" height="480" />
        </div>
        <br><br>
        <a href="http://127.0.0.1:8080" class="btn btn-back">⬅ Return to Dashboard</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

def gen():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        success, frame = cap.read()
        if not success:
            break
        detections = engine.process_frame(frame)
        for det in detections:
            x1, y1, x2, y2 = det["location"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, det["name"], (x1, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(port=5001, debug=False)
