import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os
import datetime
from tkinter import messagebox, filedialog

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EventManagement(ctk.CTk):
    def __init__(self, user_name="BLACK QUEEN"):
        super().__init__()

        self.title("🏫 Event & Club Management")
        self.geometry("950x700")
        self.minsize(800, 600)

        # State Data
        self.user_name = user_name # Dynamic logged-in user
        
        # Events Database (Empty - Add manually)
        self.events = []

        # ============ Grid Configuration ============
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header 
        self.header_frame = ctk.CTkFrame(self, height=80, fg_color="#1E1E2E", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.logo = ctk.CTkLabel(self.header_frame, text="🎉 Campus Events & Clubs", 
                                font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="#F9E2AF")
        self.logo.grid(row=0, column=0, padx=20, pady=25)
        
        self.profile = ctk.CTkLabel(self.header_frame, text=f"👤 Logged in as: {self.user_name}", 
                                   font=ctk.CTkFont(size=14), text_color="#CDD6F4")
        self.profile.grid(row=0, column=2, padx=30, pady=25, sticky="e")

        # Tabview for switching between "Upcoming Events" and "My Dashboard (Certificates)"
        self.tabview = ctk.CTkTabview(self, fg_color="#181825", corner_radius=15)
        self.tabview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_discover = self.tabview.add("Discover & Register")
        self.tab_dashboard = self.tabview.add("My Registered Events & Certificates")
        self.tab_admin = self.tabview.add("➕ Add Event (Manual)")
        
        self.tabview.set("Discover & Register")
        
        self.populate_discover_tab()
        self.populate_dashboard_tab()
        self.populate_admin_tab()

    def populate_discover_tab(self):
        # Clear existing widgets
        for widget in self.tab_discover.winfo_children():
            widget.destroy()

        self.tab_discover.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(self.tab_discover, text="Upcoming Events, Workshops & Hackathons", 
                                font=ctk.CTkFont(size=18, weight="bold"), text_color="#A6E3A1")
        title_lbl.pack(pady=(10, 20), anchor="w", padx=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self.tab_discover, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20)
        
        for ev in self.events:
            if ev["status"] == "Upcoming":
                self.create_event_card(scroll_frame, ev, is_dashboard=False)

    def populate_dashboard_tab(self):
        # Clear existing widgets
        for widget in self.tab_dashboard.winfo_children():
            widget.destroy()

        self.tab_dashboard.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(self.tab_dashboard, text="My Event History & Certificates", 
                                font=ctk.CTkFont(size=18, weight="bold"), text_color="#CBA6F7")
        title_lbl.pack(pady=(10, 20), anchor="w", padx=20)
        
        scroll_frame = ctk.CTkScrollableFrame(self.tab_dashboard, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20)
        
        # Determine if there are registered events
        registered_count = 0
        for ev in self.events:
            if ev["registered"]:
                registered_count += 1
                self.create_event_card(scroll_frame, ev, is_dashboard=True)
                
        if registered_count == 0:
            ctk.CTkLabel(scroll_frame, text="You haven't registered for any events yet.", text_color="#CDD6F4").pack(pady=30)

    def populate_admin_tab(self):
        for widget in self.tab_admin.winfo_children():
            widget.destroy()
            
        self.tab_admin.grid_columnconfigure(0, weight=1)
        
        title_lbl = ctk.CTkLabel(self.tab_admin, text="Create a New Event manually", 
                                font=ctk.CTkFont(size=18, weight="bold"), text_color="#F9E2AF")
        title_lbl.pack(pady=(20, 30))
        
        form_frame = ctk.CTkFrame(self.tab_admin, fg_color="#313244", corner_radius=10, width=500)
        form_frame.pack(pady=10, padx=20, fill="x")
        
        # Fields
        self.entry_title = ctk.CTkEntry(form_frame, placeholder_text="Event Title (e.g. AI Hackathon)", width=300)
        self.entry_title.pack(pady=(20, 10))
        
        self.entry_type = ctk.CTkOptionMenu(form_frame, values=["Hackathon", "Workshop", "Technical", "Event"], width=300)
        self.entry_type.pack(pady=10)
        
        self.entry_status = ctk.CTkOptionMenu(form_frame, values=["Upcoming", "Completed"], width=300)
        self.entry_status.pack(pady=10)
        
        self.entry_date = ctk.CTkEntry(form_frame, placeholder_text="Date (e.g. Oct 20, 2026)", width=300)
        self.entry_date.pack(pady=10)
        
        self.selected_poster = None
        self.btn_poster = ctk.CTkButton(form_frame, text="Upload Poster 🖼️ (Optional)", fg_color="#45475A", hover_color="#585B70", width=300, command=self.upload_poster)
        self.btn_poster.pack(pady=10)
        
        self.poster_lbl = ctk.CTkLabel(form_frame, text="No file selected", font=ctk.CTkFont(size=11), text_color="#A6ADC8")
        self.poster_lbl.pack(pady=(0, 10))
        
        btn_submit = ctk.CTkButton(form_frame, text="Create Event ✅", fg_color="#A6E3A1", hover_color="#94E2D5", text_color="#11111B",
                                  command=self.submit_manual_event, width=300, font=ctk.CTkFont(weight="bold"))
        btn_submit.pack(pady=(20, 30))
        
    def upload_poster(self):
        filepath = filedialog.askopenfilename(title="Select Event Poster", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if filepath:
            self.selected_poster = filepath
            filename = os.path.basename(filepath)
            self.poster_lbl.configure(text=f"Selected: {filename}", text_color="#CBA6F7")
            
    def submit_manual_event(self):
        title = self.entry_title.get().strip()
        ev_type = self.entry_type.get()
        ev_status = self.entry_status.get()
        date = self.entry_date.get().strip()
        
        if not title or not date:
            print("Please fill all fields")
            return
            
        new_event = {
            "id": len(self.events) + 1,
            "title": title,
            "type": ev_type,
            "date": date,
            "status": ev_status,
            "registered": False,
            "poster": getattr(self, "selected_poster", None)
        }
        
        self.events.append(new_event)
        print(f"Added Manual Event: {title}")
        
        # Clear fields
        self.entry_title.delete(0, 'end')
        self.entry_date.delete(0, 'end')
        self.selected_poster = None
        self.poster_lbl.configure(text="No file selected", text_color="#A6ADC8")
        
        # Refresh Discover tab
        self.populate_discover_tab()
        self.tabview.set("Discover & Register")

    def create_event_card(self, parent, event, is_dashboard=False):
        card = ctk.CTkFrame(parent, fg_color="#313244", corner_radius=10)
        card.pack(fill="x", pady=10, ipady=10)
        
        card.grid_columnconfigure(1, weight=1)
        
        # Logic for icons/colors based on type
        icon = "🎟️"
        color = "#89B4FA"
        if event["type"] == "Hackathon":
            icon = "💻"
            color = "#F38BA8"
        elif event["type"] == "Workshop":
            icon = "🛠️"
            color = "#A6E3A1"

        # Type Badge or Poster Thumbnail
        has_valid_poster = False
        if event.get("poster") and os.path.exists(event["poster"]):
            try:
                img = Image.open(event["poster"])
                # We need to preserve aspect ratio, let's create a 60x60 thumbnail
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                badge = ctk.CTkLabel(card, text="", image=ctk_img, corner_radius=8)
                has_valid_poster = True
            except Exception as e:
                print(f"Error loading poster: {e}")
                
        if not has_valid_poster:
            badge = ctk.CTkLabel(card, text=f" {icon} {event['type']} ", fg_color="#1E1E2E", text_color=color, corner_radius=8, font=ctk.CTkFont(weight="bold"))
            
        badge.grid(row=0, column=0, rowspan=2, padx=20, pady=15)
        
        # Event details
        title = ctk.CTkLabel(card, text=event["title"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#CDD6F4")
        title.grid(row=0, column=1, sticky="w", pady=(15, 0))
        
        date = ctk.CTkLabel(card, text=f"📅 Date: {event['date']}  |  📌 Status: {event['status']}", font=ctk.CTkFont(size=12), text_color="#A6ADC8")
        date.grid(row=1, column=1, sticky="w")
        
        # Action Buttons
        if not is_dashboard:
            if event["registered"]:
                btn = ctk.CTkButton(card, text="✅ Registered", state="disabled", fg_color="#45475A", text_color="#A6ADC8", width=120)
            else:
                btn = ctk.CTkButton(card, text="Register Now", fg_color="#89B4FA", hover_color="#B4BEFE", text_color="#11111B", width=120,
                                   command=lambda e=event: self.register_event(e))
            btn.grid(row=0, column=2, rowspan=2, padx=20)
        else:
            if event["status"] == "Completed":
                btn = ctk.CTkButton(card, text="📥 Download Certificate", fg_color="#CBA6F7", hover_color="#F5C2E7", text_color="#11111B", width=160,
                                   command=lambda e=event: self.generate_certificate(e))
            else:
                btn = ctk.CTkButton(card, text="⏳ Awaiting Completion", state="disabled", fg_color="#45475A", text_color="#A6ADC8", width=160)
            btn.grid(row=0, column=2, rowspan=2, padx=20)

    def register_event(self, event):
        event["registered"] = True
        
        # Show success message
        print(f"Registered for {event['title']}")
        
        # Refresh both tabs
        self.populate_discover_tab()
        self.populate_dashboard_tab()
        
        # Switch to dashboard tab to show registration
        self.tabview.set("My Registered Events & Certificates")

    def generate_certificate(self, event):
        """Creates a graphical certificate using Pillow and saves it to the user's local directory."""
        try:
            # Create a blank white image (1200x800)
            img = Image.new('RGB', (1200, 800), color='#FFFFFF')
            draw = ImageDraw.Draw(img)
            
            # Draw borders
            draw.rectangle([20, 20, 1180, 780], outline="#CBA6F7", width=15)
            draw.rectangle([35, 35, 1165, 765], outline="#89B4FA", width=5)

            # (Optional) We could load standard TTF fonts if they existed, but since we don't know the system paths reliably,
            # we'll use PIL's default proportional font (it might be small, but it works without strict dependencies).
            # For better aesthetics, I will attempt to load a generic Windows font
            try:
                title_font = ImageFont.truetype("arialbd.ttf", 60)
                sub_font = ImageFont.truetype("arial.ttf", 40)
                text_font = ImageFont.truetype("ariali.ttf", 30)
            except IOError:
                # Fallback if aerial is not found
                title_font = ImageFont.load_default()
                sub_font = ImageFont.load_default()
                text_font = ImageFont.load_default()

            # Add Text to Certificate
            draw.text((600, 150), "CERTIFICATE OF PARTICIPATION", fill="#1E1E2E", font=title_font, anchor="ms")
            draw.text((600, 250), "This is proudly presented to", fill="#45475A", font=sub_font, anchor="ms")
            
            # User Name
            draw.text((600, 350), self.user_name.upper(), fill="#F38BA8", font=title_font, anchor="ms")
            draw.line([(300, 370), (900, 370)], fill="#313244", width=3)
            
            # Event Details
            draw.text((600, 450), "For successful participation & completion of the", fill="#45475A", font=text_font, anchor="ms")
            draw.text((600, 520), event["title"], fill="#89B4FA", font=title_font, anchor="ms")
            
            draw.text((600, 600), f"Held on {event['date']}", fill="#45475A", font=sub_font, anchor="ms")

            # Signatures
            draw.text((250, 700), "____________________", fill="#1E1E2E", font=sub_font, anchor="ms")
            draw.text((250, 740), "Faculty Coordinator", fill="#45475A", font=text_font, anchor="ms")

            draw.text((950, 700), "____________________", fill="#1E1E2E", font=sub_font, anchor="ms")
            draw.text((950, 740), "Club President", fill="#45475A", font=text_font, anchor="ms")

            # Save the file
            filename = f"Certificate_{event['title'].replace(' ', '_')}.png"
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            img.save(desktop_path)
            
            print(f"Certificate downloaded to: {desktop_path}")
            
            # Open the generated image to show the user
            os.startfile(desktop_path)
            
        except Exception as e:
            print(f"Error generating certificate: {e}")

class CampusLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Campus Login")
        self.geometry("450x500")
        self.minsize(450, 500)
        
        # General Authorized Users Database (User ID -> Password)
        self.authorized_users = {
            "blackqueen": "password123",
            "admin": "admin",
            "student": "student",
            "user1": "12345"
        }

        self.frame = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=15)
        self.frame.pack(padx=40, pady=40, fill="both", expand=True)
        
        self.title_lbl = ctk.CTkLabel(self.frame, text="Welcome Back 👋", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#F9E2AF")
        self.title_lbl.pack(pady=(50, 20))
        
        self.error_lbl = ctk.CTkLabel(self.frame, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F38BA8")
        self.error_lbl.pack(pady=(0, 10))
        
        self.username = ctk.CTkEntry(self.frame, placeholder_text="User ID (e.g. blackqueen)", width=320, height=50, font=ctk.CTkFont(size=14))
        self.username.pack(pady=10)
        
        self.password = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=320, height=50, font=ctk.CTkFont(size=14))
        self.password.pack(pady=10)
        
        self.btn = ctk.CTkButton(self.frame, text="Login 🚀", width=320, height=50, corner_radius=10,
                                fg_color="#89B4FA", hover_color="#B4BEFE", text_color="#11111B", 
                                font=ctk.CTkFont(weight="bold", size=16), command=self.login)
        self.btn.pack(pady=(30, 20))
        
    def login(self):
        user = self.username.get().strip().lower()
        pwd = self.password.get().strip()
        
        if not user or not pwd:
            self.error_lbl.configure(text="⚠️ Enter both User ID and Password")
            return
            
        if user in self.authorized_users and self.authorized_users[user] == pwd:
            # Login successful
            self.destroy()
            display_name = user.title() # Capitalize user ID for the dashboard
            app = EventManagement(user_name=display_name)
            app.mainloop()
        else:
            # Login failed
            self.error_lbl.configure(text="❌ Incorrect User ID or Password")

if __name__ == "__main__":
    login_app = CampusLogin()
    login_app.mainloop()
