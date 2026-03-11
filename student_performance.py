import os
import subprocess
import sys
import time
import webbrowser

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hybrid_dir = os.path.join(current_dir, "hybrid_mental_health_project")
    
    if os.path.exists(hybrid_dir):
        print("Launching Hybrid Mental Health Project...")
        
        # Change directory so it can find 'templates', 'static', and 'hybrid_model.py'
        os.chdir(hybrid_dir)
        
        # Start the Flask app as a detached process
        subprocess.Popen([sys.executable, "app.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Give the server a few seconds to initialize
        time.sleep(3)
        
        # Open the default web browser explicitly
        webbrowser.open("http://127.0.0.1:5000")
    else:
        print("Error: hybrid_mental_health_project directory not found.")

if __name__ == "__main__":
    main()
