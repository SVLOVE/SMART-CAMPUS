import subprocess
import os
import sys
import webbrowser
import time

# Use CREATE_NO_WINDOW so absolutely ZERO terminal/cmd popups occur 
CREATE_NO_WINDOW = 0x08000000

def run_hidden_flask(script_name, folder=""):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, folder) if folder else base_dir
    script_path = os.path.join(target_dir, script_name)
    
    if os.path.exists(script_path):
        print(f"Starting hidden background service: {script_name}...")
        # Use pythonw instead of python to ensure no console flashes
        python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
        
        proc = subprocess.Popen([python_exe, script_name], 
                               cwd=target_dir, 
                               creationflags=CREATE_NO_WINDOW)
        return proc
    else:
        print(f"File not found: {script_path}")
        return None

if __name__ == "__main__":
    print("Launching Full Web Ecosystem in the background...")
    
    # 1. Start Smart Attendance API (Port 5001)
    run_hidden_flask("app.py", "Automatic_Attendance_System")
    
    # 2. Start Hybrid Mental Health API (Port 5000)
    run_hidden_flask("app.py", "hybrid_mental_health_project")
    
    # 3. Start Events & Notices API (Port 5002)
    run_hidden_flask("notice_board_web.py")
    
    # 4. Start Central Web Dashboard (Port 8080)
    run_hidden_flask("web_dashboard.py")
    
    # Allow servers 3 seconds to spin up
    print("Servers starting... opening browser in 3 seconds.")
    time.sleep(3)
    
    # Open the Central Web Dashboard in the user's default browser
    webbrowser.open("http://127.0.0.1:8080")
    print("Web application is now running on your browser!")
    print("You can close this window; the web apps will continue to run in the background.")
