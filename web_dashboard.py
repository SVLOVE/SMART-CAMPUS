from flask import Flask, render_template_string, jsonify
import subprocess
import os

app = Flask(__name__)

# Premium HTML template for the Elite Dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎓 Smart Campus - Elite Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #020204;
            --card-bg: rgba(18, 18, 24, 0.7);
            --accent-primary: #cba6f7;
            --accent-secondary: #89b4fa;
            --text-main: #ffffff;
            --text-dim: #bac2de;
            --success: #a6e3a1;
            --warning: #f9e2af;
            --danger: #f38ba8;
            --glass-border: rgba(255, 255, 255, 0.05);
            --glow-primary: rgba(203, 166, 247, 0.3);
        }

        * {
            box-sizing: border-box;
            transition: all 0.4s cubic-bezier(0.2, 1, 0.2, 1);
        }

        body {
            margin: 0;
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-deep);
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
            perspective: 1000px;
        }

        /* Ultimate Mesh Gradient + Noise Overlay */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 10% 10%, rgba(203, 166, 247, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 10%, rgba(137, 180, 250, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 50% 90%, rgba(243, 139, 168, 0.1) 0%, transparent 50%);
            z-index: -2;
            animation: meshFloat 15s infinite alternate ease-in-out;
        }

        .scanlines {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
            background-size: 100% 2px, 3px 100%;
            z-index: -1;
            pointer-events: none;
            opacity: 0.3;
        }

        @keyframes meshFloat {
            0% { transform: scale(1) translate(0, 0); }
            100% { transform: scale(1.1) translate(20px, 20px); }
        }

        /* High-Fidelity Navigation */
        .top-navbar {
            background: rgba(10, 10, 15, 0.4);
            backdrop-filter: blur(30px) saturate(180%);
            -webkit-backdrop-filter: blur(30px) saturate(180%);
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 80px;
            border-bottom: 1px solid var(--glass-border);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .logo-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 0 40px var(--glow-primary);
            animation: hoverPulse 4s infinite ease-in-out;
        }

        @keyframes hoverPulse {
            0%, 100% { transform: scale(1) rotate(-5deg); box-shadow: 0 0 20px var(--glow-primary); }
            50% { transform: scale(1.05) rotate(5deg); box-shadow: 0 0 50px var(--glow-primary); }
        }

        .logo-text {
            font-size: 24px;
            font-weight: 900;
            letter-spacing: -1px;
            text-transform: uppercase;
            background: linear-gradient(90deg, #fff, #9399b2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-center {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
        }

        .live-clock {
            font-family: 'Outfit', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: var(--accent-secondary);
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(137, 180, 250, 0.4);
        }

        .nav-actions {
            display: flex;
            align-items: center;
            gap: 30px;
        }

        .logout-btn {
            padding: 14px 32px;
            border-radius: 16px;
            background: rgba(243, 139, 168, 0.05);
            color: var(--danger);
            text-decoration: none;
            font-weight: 800;
            border: 1px solid rgba(243, 139, 168, 0.2);
            font-size: 13px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .logout-btn:hover {
            background: var(--danger);
            color: #000;
            box-shadow: 0 0 30px rgba(243, 139, 168, 0.4);
            transform: translateY(-3px);
        }

        /* Dashboard Core */
        .main-stage {
            padding: 100px 40px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .dashboard-header {
            text-align: center;
            margin-bottom: 100px;
        }

        .dashboard-header h1 {
            font-size: 64px;
            font-weight: 900;
            margin: 0 0 20px 0;
            letter-spacing: -3px;
            background: linear-gradient(to right, #fff, var(--accent-secondary), var(--accent-primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 20px rgba(255,255,255,0.1));
        }

        .dashboard-header p {
            color: var(--text-dim);
            font-size: 24px;
            margin: 0;
            font-weight: 300;
            opacity: 0.8;
        }

        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 50px;
            max-width: 1100px;
            margin: 0 auto;
        }

        /* 3D Holographic Cards */
        .module-card {
            background: var(--card-bg);
            backdrop-filter: blur(25px);
            border-radius: 40px;
            padding: 50px;
            border: 1px solid var(--glass-border);
            position: relative;
            transform-style: preserve-3d;
            animation: cardEntrance 1s cubic-bezier(0.2, 1, 0.2, 1) forwards;
            opacity: 0;
        }

        @keyframes cardEntrance {
            from { opacity: 0; transform: translateY(60px) rotateX(-10deg); }
            to { opacity: 1; transform: translateY(0) rotateX(0); }
        }

        .module-card:hover {
            transform: translateY(-20px) rotateX(5deg) scale(1.03);
            border-color: var(--card-accent);
            box-shadow: 0 50px 100px rgba(0,0,0,0.7), 0 0 50px rgba(var(--card-accent-rgb), 0.2);
        }

        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
        }

        .module-icon {
            font-size: 42px;
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.02);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--glass-border);
        }

        .status-pill {
            font-size: 11px;
            font-weight: 900;
            padding: 10px 20px;
            border-radius: 50px;
            text-transform: uppercase;
            letter-spacing: 2px;
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .heartbeat {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: currentColor;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.8); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 10px currentColor; }
            100% { transform: scale(0.8); opacity: 0.5; }
        }

        .status-online { color: var(--success); }
        .status-external { color: var(--accent-secondary); }

        .card-body h3 {
            font-size: 30px;
            margin: 0 0 20px 0;
            color: #fff;
            font-weight: 800;
            letter-spacing: -1px;
        }

        .card-body p {
            color: var(--text-dim);
            font-size: 18px;
            line-height: 1.8;
            margin-bottom: 45px;
            min-height: 70px;
        }

        .action-btn {
            display: block;
            width: 100%;
            padding: 22px;
            border-radius: 24px;
            text-align: center;
            text-decoration: none;
            font-weight: 900;
            font-size: 19px;
            background: var(--card-accent);
            color: #020204;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .action-btn:hover {
            transform: scale(1.05);
            filter: brightness(1.2);
            box-shadow: 0 20px 40px rgba(var(--card-accent-rgb), 0.5);
        }

        /* Color Assignments */
        .card-attendance { --card-accent: #a6e3a1; --card-accent-rgb: 166, 227, 161; animation-delay: 0.1s; }
        .card-analytics { --card-accent: #f9e2af; --card-accent-rgb: 249, 226, 175; animation-delay: 0.2s; }
        .card-notes { --card-accent: #f38ba8; --card-accent-rgb: 243, 139, 168; animation-delay: 0.3s; }
        .card-notice { --card-accent: #fab387; --card-accent-rgb: 250, 179, 135; animation-delay: 0.4s; }

    </style>
</head>
<body onload="startTime()">
    <div class="scanlines"></div>

    <header class="top-navbar">
        <div class="logo-area">
            <div class="logo-icon">💠</div>
            <div class="logo-text">ELITE CORE</div>
        </div>

        <div class="nav-center">
            <div id="clock" class="live-clock">00:00:00</div>
            <div style="font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 3px; margin-top: 5px;">Secure Session Active</div>
        </div>

        <div class="nav-actions">
            <div style="text-align: right;">
                <span style="font-weight: 800; font-size: 16px; color: #fff; display: block;">BLACK QUEEN</span>
                <span style="font-size: 11px; color: var(--accent-primary); letter-spacing: 1px;">ROOT ADMINISTRATOR</span>
            </div>
            <a href="#" class="logout-btn">Shutdown</a>
        </div>
    </header>

    <main class="main-stage">
        <div class="dashboard-header">
            <h1>Dynamic Command Matrix</h1>
            <p>Industrial-grade intelligent campus orchestration interface.</p>
        </div>

        <section class="grid-container">
            <!-- Attendance -->
            <div class="module-card card-attendance">
                <div class="card-top">
                    <div class="module-icon">🔒</div>
                    <div class="status-pill status-online">
                        <div class="heartbeat"></div> Operational
                    </div>
                </div>
                <div class="card-body">
                    <h3>SMART ATTENDANCE SYSTEM</h3>
                    <p>High-precision facial recognition engine with localized database synchronization.</p>
                    <a href="http://127.0.0.1:5001" class="action-btn">Link Terminal</a>
                </div>
            </div>

            <!-- Analytics -->
            <div class="module-card card-analytics">
                <div class="card-top">
                    <div class="module-icon">🧠</div>
                    <div class="status-pill status-online">
                        <div class="heartbeat"></div> Analyzing
                    </div>
                </div>
                <div class="card-body">
                    <h3>STUDENT PERFOMANCE ANALYZER</h3>
                    <p>Hybrid AI modeling for student mental health and academic performance telemetry.</p>
                    <a href="http://127.0.0.1:5000" class="action-btn">Open Cluster</a>
                </div>
            </div>

            <!-- Notes -->
            <div class="module-card card-notes">
                <div class="card-top">
                    <div class="module-icon">📓</div>
                    <div class="status-pill status-external">
                        <div class="heartbeat"></div> Syncing
                    </div>
                </div>
                <div class="card-body">
                    <h3>NOTESHARE</h3>
                    <p>Global encrypted repository for high-fidelity educational assets and archives.</p>
                    <a href="https://noteshare-kobk.onrender.com/notes" target="_blank" class="action-btn">Sync Hub</a>
                </div>
            </div>

            <!-- Notice Board -->
            <div class="module-card card-notice">
                <div class="card-top">
                    <div class="module-icon">📡</div>
                    <div class="status-pill status-online">
                        <div class="heartbeat"></div> Broadcasting
                    </div>
                </div>
                <div class="card-body">
                    <h3>SMART NOTICE BOARD</h3>
                    <p>Instantaneous campus broadcast network for administrative circulars and event alerts.</p>
                    <a href="http://127.0.0.1:5002" class="action-btn">Open Relay</a>
                </div>
            </div>
        </section>
    </main>

    <script>
        function startTime() {
            const today = new Date();
            let h = today.getHours();
            let m = today.getMinutes();
            let s = today.getSeconds();
            m = checkTime(m);
            s = checkTime(s);
            document.getElementById('clock').innerHTML = h + ":" + m + ":" + s;
            setTimeout(startTime, 1000);
        }

        function checkTime(i) {
            if (i < 10) {i = "0" + i};  // add zero in front of numbers < 10
            return i;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("Starting Web Dashboard on http://127.0.0.1:8080")
    app.run(port=8080, debug=False)
