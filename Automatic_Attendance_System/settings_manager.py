import json
import os

class SettingsManager:
    def __init__(self, data_file='settings.json'):
        self.data_file = data_file
        self.settings = self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_file):
            return {
                "profile": {
                    "admin_name": "BLACK QUEEN",
                    "admin_email": "svlove0991@gmail.com"
                },
                "notifications": {
                    "email_alerts": True,
                    "sms_alerts": True,
                    "weekly_reports": True,
                    "audio_alerts": True
                },
                "system": {
                    "total_classes": 72,
                    "auto_logout_mins": 10
                },
                "firebase": {
                    "enabled": True,
                    "database_url": "https://attendance1448-default-rtdb.asia-southeast1.firebasedatabase.app/",
                    "service_account_path": "serviceAccountKey.json"
                }
            }
        with open(self.data_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_data(self, new_settings):
        # Update current settings with new keys
        for category, values in new_settings.items():
            if category in self.settings:
                if isinstance(values, dict):
                    self.settings[category].update(values)
                else:
                    self.settings[category] = values
        
        with open(self.data_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
        return {"status": "success", "message": "Settings updated successfully."}

    def get_settings(self):
        return self.settings

settings_manager = SettingsManager()
