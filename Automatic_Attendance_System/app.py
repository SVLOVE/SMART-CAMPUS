from flask import Flask, render_template, Response, jsonify, request, send_from_directory
import cv2
import threading
import os
import csv
from datetime import datetime
from main import AttendanceEngine
from students import student_manager

app = Flask(__name__)
# Initialize the facial recognition engine
engine = AttendanceEngine()

@app.route('/api/students/photo', methods=['GET'])
def get_student_photo():
    name = request.args.get('name', '').upper()
    images_dir = os.path.abspath(getattr(engine, 'path', 'Images'))
    filename = f"{name}.jpg"
    if os.path.exists(os.path.join(images_dir, filename)):
        return send_from_directory(images_dir, filename)
    else:
        return jsonify({"status": "error", "message": "Photo not found"}), 404

# Global variables for camera
camera_active = False
cap = None

def generate_frames():
    global camera_active, cap
    
    while camera_active and cap is not None:
        success, frame = cap.read()
        if not success:
            break
            
        # Process the frame using the attendance engine
        detections = engine.process_frame(frame)
        
        # Draw bounding boxes
        for det in detections:
            x1, y1, x2, y2 = det["location"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, det["name"], (x1, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            if det["is_new"]:
                print(f"Attendance Marked for {det['name']}")
                
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield the frame for HTTP streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    if not camera_active:
        # Return a placeholder or blank image if camera is off
        # For simplicity, returning empty response when off, handled by JS
        return "", 204
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    global camera_active, cap
    if not camera_active:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return jsonify({"status": "error", "message": "Could not access webcam"}), 500
        camera_active = True
    return jsonify({"status": "success", "message": "Camera started"})

@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    global camera_active, cap
    camera_active = False
    if cap is not None:
        cap.release()
        cap = None
    return jsonify({"status": "success", "message": "Camera stopped"})

@app.route('/api/camera/status', methods=['GET'])
def camera_status():
    global camera_active
    return jsonify({"active": camera_active})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    filename = "Attendance.csv"
    logs = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                logs = list(reader)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # Sort logs by most recent first (assuming Time or Date can be sorted natively, reverse list)
    logs.reverse()
    return jsonify({"status": "success", "data": logs})

@app.route('/api/attendance/manual', methods=['POST'])
def manual_attendance():
    data = request.json
    name = data.get('name')
    if not name:
         return jsonify({"status": "error", "message": "Name is required"}), 400
         
    is_new = engine.mark_attendance(name=name.upper(), status="Manual Sign-In")
    if is_new:
        student_manager.update_attendance_count(name)
        return jsonify({"status": "success", "message": f"Manual attendance marked for {name}"})
    else:
         return jsonify({"status": "info", "message": f"{name} is already marked present today"})

@app.route('/api/students/enroll', methods=['POST'])
def enroll_student():
    data = request.form
    photo = request.files.get('photo')
    
    if not photo:
        return jsonify({"status": "error", "message": "Photo is required for enrollment"}), 400

    name = data.get('name', '')
    
    result = student_manager.enroll_student(
        name=name,
        roll_no=data.get('roll_no', ''),
        dept=data.get('dept', ''),
        age=data.get('age', ''),
        email=data.get('email', '')
    )
    
    if result['status'] == 'success':
        # Save photo
        images_dir = getattr(engine, 'path', 'Images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            
        # Secure the filename using the student's name
        filename = f"{name.upper()}.jpg"
        filepath = os.path.join(images_dir, filename)
        photo.save(filepath)
        
        # Reload facial recognition encodings so this person is recognized instantly
        try:
            engine.load_and_encode()
        except Exception as e:
            print(f"Error reloading encodings: {e}")
            
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/students/get', methods=['GET'])
def get_student_details():
    name = request.args.get('name', '')
    details = student_manager.load_data().get(name.upper())
    if details:
        return jsonify({"status": "success", "data": details})
    else:
        return jsonify({"status": "error", "message": "Student not found"}), 404

@app.route('/api/students/edit', methods=['POST'])
def edit_student_api():
    data = request.json
    orig_name = data.get('original_name', '')
    new_name = data.get('new_name', '')
    
    result = student_manager.edit_student(
        original_name=orig_name,
        new_name=new_name,
        roll_no=data.get('roll_no', ''),
        dept=data.get('dept', ''),
        age=data.get('age', ''),
        email=data.get('email', '')
    )
    
    if result['status'] == 'success':
        # Rename image file if name changed
        if orig_name.upper() != new_name.upper():
            images_dir = getattr(engine, 'path', 'Images')
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
            old_path = os.path.join(images_dir, f"{orig_name.upper()}.jpg")
            new_path = os.path.join(images_dir, f"{new_name.upper()}.jpg")
            if os.path.exists(old_path):
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    print(f"Error renaming image: {e}")
            
            # Re-encode faces
            try:
                engine.load_and_encode()
            except Exception as e:
                print(f"Error reloading encodings: {e}")

        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/students/progress', methods=['GET'])
def student_progress():
    progress = student_manager.get_progress_report(total_classes=30)
    return jsonify({"status": "success", "data": progress})

from settings_manager import settings_manager

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({"status": "success", "data": settings_manager.get_settings()})

@app.route('/api/settings', methods=['POST'])
def save_settings():
    new_settings = request.json
    result = settings_manager.save_data(new_settings)
    return jsonify(result)

@app.route('/api/camera/last_recognized', methods=['GET'])
def last_recognized():
    last_name = getattr(engine, 'last_recognized_student', None)
    if not last_name:
        return jsonify({"status": "no_match"})
    
    details = student_manager.get_student(last_name)
    if details:
        return jsonify({"status": "success", "data": details})
    else:
        return jsonify({"status": "partial", "data": {"name": last_name}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
