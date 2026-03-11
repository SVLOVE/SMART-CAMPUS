import firebase_admin
from firebase_admin import credentials, db
import os
import json

class FirebaseManager:
    def __init__(self):
        self.app = None
        self.initialized = False

    def initialize(self, service_account_path, database_url):
        if self.initialized:
            return True
        
        if not os.path.exists(service_account_path):
            print(f"Firebase error: Service account file not found at {service_account_path}")
            return False

        try:
            cred = credentials.Certificate(service_account_path)
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            self.initialized = True
            print("Firebase initialized successfully.")
            return True
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            return False

    def upload_attendance(self, student_data):
        if not self.initialized:
            from settings_manager import settings_manager
            settings = settings_manager.get_settings()
            fb_settings = settings.get('firebase', {})
            if fb_settings.get('enabled'):
                if not self.initialize(fb_settings.get('service_account_path'), fb_settings.get('database_url')):
                    return False
            else:
                return False

        try:
            # We'll use the student's name as a key or create a log entry with timestamp
            ref = db.reference('attendance_logs')
            new_log_ref = ref.push()
            new_log_ref.set(student_data)
            print(f"Attendance for {student_data.get('Name')} uploaded to Firebase.")
            return True
        except Exception as e:
            print(f"Firebase upload failed: {e}")
            return False

firebase_manager = FirebaseManager()
