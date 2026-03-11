# Automatic Attendance System - GUI Walkthrough

The Automatic Attendance System has been upgraded from a terminal-only script to a professional Graphical User Interface (GUI) dashboard. This walkthrough details the new features and how to use them.

## New Project Structure
The project is now organized into two main files to keep the interface and the logic separate:
- `main.py`: Contains the `AttendanceEngine` class (the "brain" that handles face recognition).
- `gui.py`: The new entry point that launches the visual dashboard.
- `Images/`: Still contains your enrollment photos.
- `Attendance.csv`: The automatically generated log file.

## Key Features & Usage

### 1. Interactive Dashboard
The system now launches directly into the dashboard for immediate use.
- **One-Click Controls**: Use the side panel to start/stop the recognition engine.
- **Real-Time Data**: Live status labels and name overlays provide instant feedback.

### 1. Live Camera Feed
The central part of the window displays the real-time webcam feed.
- **Bounding Boxes**: Green boxes appear around recognized faces.
- **Name Overlay**: The recognized name is displayed directly on the video.

### 2. Rainbow Attendance Viewer
The attendance logs now feature a vibrant "Rainbow" styling for better data tracking.
- **Color-Coded Headers**: Each column has a distinct, bright color to help your eyes track data vertically.
- **Zebra Striping**: Alternating white and grey rows make it easy to follow a single record across the screen.
- **Vibrant UI**: Updated with a clean modern look and easy-to-use refresh button.

### 3. Advanced RBQL Search
The Attendance Viewer now includes a powerful SQL-style search engine:
- **How to Query**: Use `a1` to `a10` for columns.
  - `a1`: Name | `a2`: Roll No | `a3`: Dept
  - `a4`: Date | `a5`: Time | `a6`: Status
  - `a7`: **Blood Group** | `a8`: **DOB** | `a9`: **Age** | `a10`: **Gender**
- **Examples**:
  - Filter by Blood Group: `SELECT * WHERE a7 == 'B+'`
  - Find by Age: `SELECT * WHERE a9 == '20'`
  - Search by Dept: `SELECT * WHERE a3 == 'AI&DS'`

### 3. Control Dashboard
- **START CAMERA**: Initializes the webcam and starts the recognition engine.
- **STOP CAMERA**: Safely releases the webcam and halts processing.

### 4. Management Tools
- **OVERALL ATTENDANCE**: Launches the new table viewer described above.
- **MANUAL SIGN-IN**: A new feature that allows you to manually enter a name to mark attendance without facial recognition. This is perfect for guests or if someone's photo isn't in the system.
- **VIEW LOGS (CSV)**: Instantly opens your `Attendance.csv` file (Excel/CSV).
- **MANAGE IMAGES**: Opens the `Images` folder in Windows Explorer so you can quickly add new people.

### 4. Real-time Status
- The dashboard shows a **System Status** (e.g., "Scanning...") and a **Last Recognized** label that updates the moment a match is found.

## How to Run
To launch the new interface, use the following command in your terminal:
```powershell
py -3.11 gui.py
```

---
*Note: Make sure to close the camera using the "STOP CAMERA" button before closing the window to ensure the webcam is released for other apps.*
