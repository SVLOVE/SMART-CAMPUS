import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

class AttendanceEngine:
    def __init__(self, images_path='Images'):
        self.path = images_path
        self.images = []
        self.classNames = []
        self.encodeListKnown = []
        self.last_recognized_student = None
        self.load_and_encode()

    def load_and_encode(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            print(f"Created {self.path} folder.")
            return

        myList = os.listdir(self.path)
        for cl in myList:
            curImg = cv2.imread(f'{self.path}/{cl}')
            if curImg is not None:
                self.images.append(curImg)
                self.classNames.append(os.path.splitext(cl)[0])

        self.encodeListKnown = self.find_encodings(self.images)
        print(f"Loaded {len(self.classNames)} images and completed encoding.")

    def find_encodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodes = face_recognition.face_encodings(img)
            if len(encodes) > 0:
                encodeList.append(encodes[0])
        return encodeList

    def mark_attendance(self, name, roll_no="N/A", dept="N/A", status="Auto-Detected", blood_group="N/A", dob="N/A", age="N/A", gender="N/A"):
        filename = "Attendance.csv"
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8-sig") as f:
                f.write("Name,Roll No,Department,Date,In Time,Out Time,Status,Blood Group,DOB,Age,Gender\n")

        now = datetime.now()
        dateString = now.strftime('%Y-%m-%d')
        timeString = now.strftime('%H:%M:%S')

        try:
            with open(filename, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        updated = False
        is_new = False
        
        for i, line in enumerate(lines):
            parts = line.strip().split(',')
            if len(parts) >= 6 and i > 0:
                lname = parts[0]
                ldate = parts[3]
                if lname == name and ldate == dateString:
                    # Pad if necessary
                    while len(parts) < 11:
                        parts.append("N/A")
                    parts[5] = timeString # Update Out Time
                    lines[i] = ','.join(parts) + '\n'
                    updated = True
                    break

        if not updated:
            from students import student_manager
            student = student_manager.get_student(name)
            if student:
                roll_no = student.get('roll_no', roll_no)
                dept = student.get('dept', dept)
                age = student.get('age', age)
                
            new_line = f'{name},{roll_no},{dept},{dateString},{timeString},N/A,{status},{blood_group},{dob},{age},{gender}\n'
            # Ensure the last line has a newline
            if lines and not lines[-1].endswith('\n'):
                lines[-1] = lines[-1] + '\n'
            lines.append(new_line)
            is_new = True
            
            # Automated workflow trigger
            student_manager.update_attendance_count(name)

        if is_new or updated:
            with open(filename, "w", encoding="utf-8-sig") as f:
                f.writelines(lines)

        if is_new:
            # Firebase Export
            try:
                from firebase_manager import firebase_manager
                firebase_manager.upload_attendance({
                    "Name": name,
                    "Roll No": roll_no,
                    "Department": dept,
                    "Date": dateString,
                    "In Time": timeString,
                    "Out Time": "N/A",
                    "Status": status,
                    "Age": age
                })
            except Exception as e:
                print(f"Firebase Sync Trigger Failed: {e}")
            return True

        return False

    def process_frame(self, frame):
        # Resize for speed
        imgSmall = cv2.resize(frame, (0,0), None, 0.25, 0.25)
        imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)
        imgSmall = np.ascontiguousarray(imgSmall)

        facesCurFrame = face_recognition.face_locations(imgSmall)
        encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)

        results = []
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)

            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = self.classNames[matchIndex].upper()
                    self.last_recognized_student = name
                    
                    # Scale face locations back up
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    
                    # Mark attendance
                    is_new = self.mark_attendance(name)
                    
                    results.append({
                        "name": name,
                        "location": (x1, y1, x2, y2),
                        "is_new": is_new
                    })
        return results

if __name__ == "__main__":
    # Test block for standalone execution if needed
    engine = AttendanceEngine()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    while True:
        success, img = cap.read()
        if not success: break
        
        detections = engine.process_frame(img)
        for det in detections:
            x1, y1, x2, y2 = det["location"]
            cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(img, det["name"], (x1,y2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
            if det["is_new"]:
                print(f"Attendance Marked for {det['name']}")
                
        cv2.imshow("Testing Engine", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
