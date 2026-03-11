import json
import os
from datetime import datetime

class StudentManager:
    def __init__(self, data_file='students.json'):
        self.data_file = data_file
        self.students = self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_file):
            return {}
        with open(self.data_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.students, f, indent=4)

    def enroll_student(self, name, roll_no, dept, age, email):
        # Data Validation Rules
        name = name.upper()
        if name in self.students:
            return {"status": "error", "message": "Student already enrolled."}
        
        if not roll_no.isalnum():
            return {"status": "error", "message": "Roll No must be alphanumeric."}
        
        try:
            age_int = int(age)
            if age_int < 16:
                return {"status": "error", "message": "Student must be at least 16 years old."}
        except ValueError:
            return {"status": "error", "message": "Age must be a valid number."}
            
        if "@" not in email or "." not in email:
            return {"status": "error", "message": "Invalid email format."}

        self.students[name] = {
            "name": name,
            "roll_no": roll_no,
            "dept": dept,
            "age": age_int,
            "email": email,
            "enrollment_date": datetime.now().strftime("%Y-%m-%d"),
            "attendance_count": 0
        }
        self.save_data()
    def edit_student(self, original_name, new_name, roll_no, dept, age, email):
        original_name = original_name.upper()
        new_name = new_name.upper()

        if original_name not in self.students:
            return {"status": "error", "message": "Student not found."}

        # If name is changing, check if new name already exists
        if original_name != new_name and new_name in self.students:
             return {"status": "error", "message": "A student with the new name already exists."}

        # Validate other fields (optional but good for consistency)
        if not roll_no.isalnum():
            return {"status": "error", "message": "Roll No must be alphanumeric."}
        
        try:
            age_int = int(age)
            if age_int < 16:
                return {"status": "error", "message": "Student must be at least 16 years old."}
        except ValueError:
            return {"status": "error", "message": "Age must be a valid number."}
            
        if "@" not in email or "." not in email:
            return {"status": "error", "message": "Invalid email format."}

        # Update data
        student_data = self.students.pop(original_name)
        student_data.update({
            "name": new_name,
            "roll_no": roll_no,
            "dept": dept,
            "age": age_int,
            "email": email
        })
        self.students[new_name] = student_data
        
        self.save_data()
        return {"status": "success", "message": f"{new_name} updated successfully.", "old_name": original_name, "new_name": new_name}

    def get_student(self, name):
        return self.students.get(name.upper())

    def update_attendance_count(self, name):
        name = name.upper()
        if name in self.students:
            self.students[name]["attendance_count"] += 1
            self.save_data()

    def get_progress_report(self, total_classes=30): 
        # Grading Algorithm & Automated Workflow Logic
        report = []
        for name, data in self.students.items():
            att_count = data["attendance_count"]
            percentage = (att_count / total_classes) * 100 if total_classes > 0 else 0
            
            # Grading Algorithm
            if percentage >= 90:
                grade = 'A'
            elif percentage >= 75:
                grade = 'B'
            elif percentage >= 60:
                grade = 'C'
            else:
                grade = 'F'
                
            # Automated Workflow Status
            workflow = "On Track"
            if percentage < 60:
                workflow = "Disciplinary Follow-up"
            elif percentage < 75:
                workflow = "Warning Email Sent"
                
            report.append({
                "name": data["name"],
                "roll_no": data["roll_no"],
                "dept": data["dept"],
                "attendance_percentage": round(percentage, 2),
                "grade": grade,
                "workflow_status": workflow
            })
        return report

student_manager = StudentManager()
