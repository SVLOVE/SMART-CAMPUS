import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from PIL import Image, ImageTk
import os
import csv
import subprocess
import rbql
from main import AttendanceEngine

class AttendanceGUI:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("950x800")
        self.window.configure(bg="#2c3e50")

        # Initialize Engine
        self.engine = AttendanceEngine()
        
        # State variables
        self.is_running = False
        self.video_source = 0
        self.vid = None
        
        # UI Frames
        self.dashboard_frame = None
        self.setup_dashboard()


    def setup_dashboard(self):
        self.dashboard_frame = tk.Frame(self.window, bg="#2c3e50")
        self.dashboard_frame.pack(expand=True, fill=tk.BOTH)

        header = tk.Frame(self.dashboard_frame, bg="#34495e", pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="Attendance Dashboard", font=("Helvetica", 22, "bold"), bg="#34495e", fg="white").pack(side=tk.LEFT, padx=30)

        main_layout = tk.Frame(self.dashboard_frame, bg="#2c3e50", padx=20, pady=20)
        main_layout.pack(expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(main_layout, width=640, height=480, bg="black", highlightthickness=2, highlightbackground="#3498db")
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        control_panel = tk.Frame(main_layout, bg="#34495e", padx=20, pady=20)
        control_panel.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

        self.btn_start = tk.Button(control_panel, text="START CAMERA", command=self.start_camera, width=20, height=2, bg="#27ae60", fg="white", font=("Helvetica", 10, "bold"), relief=tk.FLAT)
        self.btn_start.pack(pady=10)
        self.btn_stop = tk.Button(control_panel, text="STOP CAMERA", command=self.stop_camera, width=20, height=2, bg="#e74c3c", fg="white", font=("Helvetica", 10, "bold"), relief=tk.FLAT, state=tk.DISABLED)
        self.btn_stop.pack(pady=10)

        tk.Label(control_panel, text="Data & Files", bg="#34495e", fg="#95a5a6", font=("Helvetica", 10, "italic")).pack(pady=(20, 5))
        tk.Button(control_panel, text="OVERALL ATTENDANCE", command=self.show_overall_attendance, width=20, height=2, bg="#f39c12", fg="white", font=("Helvetica", 9, "bold"), relief=tk.FLAT).pack(pady=5)
        tk.Button(control_panel, text="MANUAL SIGN-IN", command=self.manual_sign_in, width=20, height=2, bg="#9b59b6", fg="white", font=("Helvetica", 9, "bold"), relief=tk.FLAT).pack(pady=5)
        tk.Button(control_panel, text="OPEN CSV FILE", command=self.open_logs, width=20, bg="#3498db", fg="white", relief=tk.FLAT).pack(pady=5)
        tk.Button(control_panel, text="MANAGE IMAGES", command=self.open_images_folder, width=20, bg="#3498db", fg="white", relief=tk.FLAT).pack(pady=5)

        self.status_label = tk.Label(self.dashboard_frame, text="System Ready", bg="#2c3e50", fg="#ecf0f1", font=("Helvetica", 12))
        self.status_label.pack(pady=10)
        self.last_recognized_label = tk.Label(self.dashboard_frame, text="Last Recognized: None", bg="#2c3e50", fg="#f1c40f", font=("Helvetica", 14, "bold"))
        self.last_recognized_label.pack(pady=5)

    def manual_sign_in(self):
        name = simpledialog.askstring("Manual Sign-In", "Enter person's name:")
        if name:
            name = name.strip()
            if name:
                roll_no = simpledialog.askstring("Manual Sign-In", f"Enter Roll No for {name}:") or "N/A"
                dept = simpledialog.askstring("Manual Sign-In", f"Enter Department for {name}:") or "N/A"
                blood = simpledialog.askstring("Manual Sign-In", f"Enter Blood Group for {name}:") or "N/A"
                dob = simpledialog.askstring("Manual Sign-In", f"Enter DOB (YYYY-MM-DD) for {name}:") or "N/A"
                age = simpledialog.askstring("Manual Sign-In", f"Enter Age for {name}:") or "N/A"
                gender = simpledialog.askstring("Manual Sign-In", f"Enter Gender for {name}:") or "N/A"
                
                try:
                    is_new = self.engine.mark_attendance(name, roll_no=roll_no, dept=dept, status="Manual Entry", 
                                                       blood_group=blood, dob=dob, age=age, gender=gender)
                    if is_new:
                        messagebox.showinfo("Success", f"Attendance marked for {name}")
                        self.last_recognized_label.config(text=f"Last Recognized: {name.upper()}")
                    else:
                        messagebox.showinfo("Info", f"{name} is already marked for today.")
                except PermissionError:
                    messagebox.showerror("Error", "Could not save record because Attendance.csv is open in another program (like Excel). Please close it and try again.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to mark attendance: {str(e)}")

    def show_overall_attendance(self):
        viewer = tk.Toplevel(self.window)
        viewer.title("Rainbow Attendance Log - RBQL Powered")
        viewer.geometry("1100x650")
        viewer.configure(bg="#2c3e50")

        header_frame = tk.Frame(viewer, bg="#34495e", pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="🔍 RBQL Advanced Query Viewer", font=("Helvetica", 18, "bold"), bg="#34495e", fg="white").pack()

        # Query UI Bar
        query_frame = tk.Frame(viewer, bg="#2c3e50", pady=10)
        query_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(query_frame, text="Type SQL Query:", bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        query_entry = tk.Entry(query_frame, font=("Consolas", 11), bg="#34495e", fg="#2ecc71", insertbackground="white", relief=tk.FLAT)
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=5)
        query_entry.insert(0, "SELECT *")

        # Rainbow Color Palette for Columns
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c", "#95a5a6", "#d35400", "#c0392b"]
        column_names = ("Name", "Roll No", "Department", "Date", "In Time", "Out Time", "Status", "Blood Group", "DOB", "Age", "Gender")

        style = ttk.Style(viewer)
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", foreground="#333333", fieldbackground="#ffffff", rowheight=30, font=("Helvetica", 10))
        
        table_frame = tk.Frame(viewer, bg="#2c3e50", padx=10, pady=10)
        table_frame.pack(expand=True, fill=tk.BOTH)

        tree = ttk.Treeview(table_frame, columns=column_names, show="headings", height=13)
        
        for idx, col in enumerate(column_names):
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)

        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#34495e", foreground="white")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree.tag_configure('oddrow', background='#f2f2f2')
        tree.tag_configure('evenrow', background='#ffffff')

        def run_query(query_text=None):
            for item in tree.get_children(): tree.delete(item)
            filename = "Attendance.csv"
            if not os.path.exists(filename): return

            query = query_text or query_entry.get().strip()
            
            try:
                # Use RBQL to process the CSV in-memory
                input_data = []
                with open(filename, "r") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    # Pad each row to 10 columns for RBQL stability
                    for row in reader:
                        padded_row = row + ["N/A"] * (11 - len(row))
                        input_data.append(padded_row[:11])

                # Process query
                output_data = []
                error_info = None

                # a1, a2... mapping
                def rbql_query_list(query, input_list):
                    output_list = []
                    # Simple RBQL execution for lists (a1 to a10)
                    user_query = query.replace("SELECT *", "SELECT a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11")
                    try:
                        rbql.query_table(user_query, input_list, output_list, [], [])
                        return output_list, None
                    except Exception as e:
                        return [], str(e)

                res_data, err = rbql_query_list(query, input_data)
                
                if err:
                    messagebox.showwarning("Query Error", f"RBQL Error: {err}\n\nHint: Use a1 to a11 for columns.")
                    return

                for count, row in enumerate(res_data):
                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    tree.insert("", tk.END, values=row, tags=(tag,))

            except Exception as e:
                messagebox.showerror("Error", f"Failed to run query: {str(e)}")

        btn_run = tk.Button(query_frame, text="RUN QUERY", command=run_query, bg="#3498db", fg="white", relief=tk.FLAT, font=("Helvetica", 9, "bold"), padx=15)
        btn_run.pack(side=tk.RIGHT)

        button_frame = tk.Frame(viewer, bg="#2c3e50")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="🔄 RESET / REFRESH", command=lambda: [query_entry.delete(0, tk.END), query_entry.insert(0, "SELECT *"), run_query()], 
                  bg="#27ae60", fg="white", relief=tk.FLAT, pady=8, font=("Helvetica", 10, "bold"), width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Label(viewer, text="Tip: Columns a1-a11 (Name, Roll, Dept, Date, In Time, Out Time, Status, Blood, DOB, Age, Gender).", 
                 bg="#2c3e50", fg="#bdc3c7", font=("Helvetica", 9, "italic")).pack(pady=(0, 10))

        run_query("SELECT *")


    def start_camera(self):
        if not self.is_running:
            self.vid = cv2.VideoCapture(self.video_source, cv2.CAP_DSHOW)
            if not self.vid.isOpened():
                messagebox.showerror("Error", "Could not open camera.")
                return
            self.is_running = True
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.status_label.config(text="Scanning...", fg="#2ecc71")
            self.update_video()

    def stop_camera(self):
        if self.is_running:
            self.is_running = False
            if self.vid: self.vid.release()
            self.canvas.delete("all")
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.status_label.config(text="Camera Stopped", fg="#e74c3c")

    def update_video(self):
        if self.is_running:
            success, frame = self.vid.read()
            if success:
                try:
                    detections = self.engine.process_frame(frame)
                    for det in detections:
                        x1, y1, x2, y2 = det["location"]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, det["name"], (x1, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        if det["is_new"]:
                            self.last_recognized_label.config(text=f"Last Recognized: {det['name']}")

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                except Exception as e:
                    self.status_label.config(text=f"Engine Error: {str(e)}", fg="orange")
            
            self.window.after(10, self.update_video)

    def open_logs(self):
        filename = "Attendance.csv"
        if os.path.exists(filename):
            try:
                os.startfile(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open CSV file: {str(e)}")
        else:
            messagebox.showinfo("Info", "No attendance records found.")

    def open_images_folder(self):
        path = "Images"
        if not os.path.exists(path): os.makedirs(path)
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    AttendanceGUI(root, "Automatic Attendance System v1.4")
    root.mainloop()
