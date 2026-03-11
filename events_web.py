from flask import Flask, render_template_string

app = Flask(__name__)

# Basic Event DB
events = [
    {"title": "AI Hackathon", "type": "Hackathon", "date": "Oct 20, 2026", "status": "Upcoming"},
    {"title": "Python Workshop", "type": "Workshop", "date": "Nov 15, 2026", "status": "Upcoming"},
    {"title": "Tech Talk: Cybersecurity", "type": "Technical", "date": "Dec 05, 2026", "status": "Upcoming"}
]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Notice Board</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #1e1e2e; color: #cdd6f4; margin: 0; padding: 0; }
        .header { background: #181825; padding: 20px; font-size: 24px; color: #fab387; font-weight: bold; border-bottom: 2px solid #fab387; text-align: center; }
        .container { padding: 40px; max-width: 800px; margin: auto; }
        .card { background: #313244; padding: 20px; border-radius: 12px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .title { font-size: 20px; font-weight: bold; color: #fab387; }
        .details { font-size: 14px; color: #a6adc8; margin-top: 5px; }
        .badge { background: #45475a; padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; }
        .btn-back { display: block; width: 200px; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; text-decoration: none; color: #11111b; background: #89b4fa; margin: 30px auto; }
        .btn-back:hover { background: #b4befe; }
    </style>
</head>
<body>
    <div class="header">📢 Smart Campus Notice Board & Events</div>
    <div class="container">
        <h2>Upcoming Events</h2>
        {% for ev in events %}
        <div class="card">
            <div>
                <div class="title">{{ ev.title }}</div>
                <div class="details">📅 {{ ev.date }} | 📌 {{ ev.status }}</div>
            </div>
            <div class="badge">{{ ev.type }}</div>
        </div>
        {% endfor %}
        <a href="http://127.0.0.1:8080" class="btn-back">⬅ Return to Dashboard</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, events=events)

if __name__ == '__main__':
    app.run(port=5002, debug=False)
