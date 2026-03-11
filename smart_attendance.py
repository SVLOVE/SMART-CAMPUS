import os
import subprocess
import sys

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    attendance_dir = os.path.join(current_dir, "Automatic_Attendance_System")
    
    if os.path.exists(attendance_dir):
        print("Launching Smart Attendance System...")
        # Change directory so the script can find its relative files
        os.chdir(attendance_dir)
        subprocess.Popen([sys.executable, "gui.py"])
    else:
        print("Error: Automatic_Attendance_System directory not found.")

if __name__ == "__main__":
    main()
