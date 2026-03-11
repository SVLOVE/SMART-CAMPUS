from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📢 Smart Notice Board</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #0a0a0f;
            --card-bg: rgba(25, 25, 35, 0.7);
            --accent-primary: #cba6f7;
            --accent-secondary: #89b4fa;
            --text-main: #cdd6f4;
            --text-dim: #a6adc8;
            --glow: rgba(203, 166, 247, 0.2);
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(203, 166, 247, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(137, 180, 250, 0.05) 0%, transparent 40%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .header {
            text-align: center;
            margin-bottom: 50px;
        }

        .header h1 {
            font-size: 3rem;
            margin: 0;
            background: linear-gradient(45deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }

        .header p {
            color: var(--text-dim);
            font-size: 1.1rem;
            margin-top: 10px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 30px;
            width: 100%;
            max-width: 1100px;
            padding: 20px;
            box-sizing: border-box;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 40px;
            text-align: center;
            text-decoration: none;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at top right, rgba(250, 179, 135, 0.1), transparent);
            opacity: 0;
            transition: opacity 0.4s;
        }

        .card:hover {
            transform: translateY(-10px);
            border-color: var(--accent-primary);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px var(--glow);
        }

        .card:hover::before {
            opacity: 1;
        }

        .icon-box {
            width: 80px;
            height: 80px;
            background: rgba(250, 179, 135, 0.1);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            margin-bottom: 25px;
            color: var(--accent-primary);
            transition: transform 0.4s;
        }

        .card:hover .icon-box {
            transform: scale(1.1) rotate(5deg);
            background: var(--accent-primary);
            color: #11111b;
        }

        .card h2 {
            margin: 0;
            font-size: 1.6rem;
            color: #fff;
            margin-bottom: 12px;
        }

        .card p {
            margin: 0;
            color: var(--text-dim);
            font-size: 1rem;
            line-height: 1.5;
        }

        .back-btn {
            margin-top: 60px;
            padding: 12px 30px;
            background: transparent;
            border: 1px solid #45475a;
            color: var(--text-dim);
            border-radius: 12px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .back-btn:hover {
            background: #1e1e2e;
            color: #fff;
            border-color: #f9e2af;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>Smart Notice Board</h1>
        <p>Stay updated with the latest campus activities and formal announcements</p>
    </div>

    <div class="grid">
        <!-- Circulars Card -->
        <a href="https://noteshare-kobk.onrender.com/circulars" class="card" target="_blank">
            <div class="icon-box">📜</div>
            <h2>Circulars</h2>
            <p>Official administrative updates, holiday notices, and important campus instructions.</p>
        </a>

        <!-- Inter College Events Card -->
        <a href="https://noteshare-kobk.onrender.com/inter" class="card" target="_blank">
            <div class="icon-box">🏆</div>
            <h2>Inter College Events</h2>
            <p>Collaborate and compete with students from other institutions in regional and national events.</p>
        </a>

        <!-- Intra College Events Card -->
        <a href="https://noteshare-kobk.onrender.com/intra" class="card" target="_blank">
            <div class="icon-box">🏟️</div>
            <h2>Intra College Events</h2>
            <p>Explore internal competitions, club activities, and talent hunts within our campus.</p>
        </a>
    </div>

    <a href="http://127.0.0.1:8080" class="back-btn">
        <span>←</span> Back to Main Dashboard
    </a>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Use port 5002 as expected by the main dashboard
    app.run(port=5002, debug=False)
