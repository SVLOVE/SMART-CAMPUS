import customtkinter as ctk
import subprocess
import os
import webbrowser

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MainDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎓 Smart Campus - Main Dashboard")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # ============ Grid Configuration ============
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ============ Sidebar ============
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1E1E2E")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Smart Campus\nPlatform 🚀", 
                                      font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
                                      text_color="#F9E2AF")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.desc_label = ctk.CTkLabel(self.sidebar_frame, text="Centralized Student Portal",
                                      font=ctk.CTkFont(size=12), text_color="#CDD6F4")
        self.desc_label.grid(row=1, column=0, padx=20, pady=(0, 30))
        
        # Profile Mock
        self.profile_btn = ctk.CTkButton(self.sidebar_frame, text="👤 Profile Settings", fg_color="#313244", hover_color="#45475A", text_color="#CDD6F4")
        self.profile_btn.grid(row=2, column=0, padx=20, pady=10)

        self.logout_btn = ctk.CTkButton(self.sidebar_frame, text="🚪 Logout", fg_color="#F38BA8", hover_color="#F9E2AF", text_color="#11111B")
        self.logout_btn.grid(row=3, column=0, padx=20, pady=10)


        # ============ Main Area ============
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="#181825", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # 3 columns for the grid
        self.main_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.header = ctk.CTkLabel(self.main_frame, text="Welcome to your Campus Dashboard! Choose a module:", 
                                  font=ctk.CTkFont(size=20, weight="bold"), text_color="#A6E3A1")
        self.header.grid(row=0, column=0, columnspan=3, pady=(20, 30), sticky="w", padx=20)

        self.features = [
            {"id": "1", "title": "🔐 Smart Attendance", "color": "#A6E3A1", "script": "smart_attendance.py", "is_url": False},
            {"id": "2", "title": "📊 Student Performance Analytics", "color": "#F9E2AF", "script": "student_performance.py", "is_url": False},
            {"id": "3", "title": "🧾 Assignment & Notes Hub", "color": "#F38BA8", "script": "https://noteshare-kobk.onrender.com/notes", "is_url": True},
            {"id": "5", "title": "📢 Smart Notice Board", "color": "#FAB387", "script": "http://127.0.0.1:5002", "is_url": True},
        ]

        # Draw the Grid layout
        row_idx = 1
        col_idx = 0
        for feat in self.features:
            self.create_dashboard_card(feat, row_idx, col_idx)
            col_idx += 1
            if col_idx > 2:
                col_idx = 0
                row_idx += 1

    def create_dashboard_card(self, feature, r, c):
        # Card Container
        card = ctk.CTkFrame(self.main_frame, fg_color="#313244", corner_radius=15)
        card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)
        
        # Badge
        is_active = feature["script"] is not None
        status_text = "🟢 Active" if is_active else "🚧 Coming Soon"
        status_color = "#A6E3A1" if is_active else "#F38BA8"
        
        status_lbl = ctk.CTkLabel(card, text=status_text, text_color=status_color, font=ctk.CTkFont(size=11, weight="bold"))
        status_lbl.pack(pady=(15, 5), anchor="e", padx=15)

        # Title
        title_lbl = ctk.CTkLabel(card, text=feature["title"], font=ctk.CTkFont(size=15, weight="bold"), text_color=feature["color"], wraplength=200)
        title_lbl.pack(pady=(10, 20), padx=10)

        # Button
        state = "normal" if is_active else "disabled"
        btn_text = "Launch Module 🚀" if is_active else "Not Available"
        btn_color = feature["color"] if is_active else "#45475A"
        txt_color = "#11111B" if is_active else "#A6ADC8"

        btn = ctk.CTkButton(card, text=btn_text, fg_color=btn_color, hover_color="#B4BEFE", text_color=txt_color,
                           font=ctk.CTkFont(weight="bold"), state=state,
                           command=lambda f=feature: self.launch_script(f))
        btn.pack(pady=(0, 20), padx=15)

    def launch_script(self, feature):
        import sys
        script_name = feature["script"]
        is_url = feature.get("is_url", False)

        if is_url:
            print(f"Opening URL: {script_name}")
            webbrowser.open(script_name)
        elif script_name and os.path.exists(script_name):
            print(f"Launching {script_name}...")
            # Run the python script using the exact same python executable as the dashboard
            subprocess.Popen([sys.executable, script_name])
        else:
            print("Module not found or not built yet!")

if __name__ == "__main__":
    app = MainDashboard()
    app.mainloop()
