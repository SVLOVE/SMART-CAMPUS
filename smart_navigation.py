from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Mock Campus Data
CAMPUS_LOCATIONS = {
    "Outdoor": ["Canteen", "Auditorium", "Parking Area", "Administrative Office", "Main Gate"],
    "Academic Building": {
        "Ground Floor": ["Admission Office", "Reception", "Staff Room"],
        "First Floor": ["Classroom A101", "Classroom A102", "Physics Lab"],
        "Second Floor": ["Computer Lab 1", "Computer Lab 2", "Seminar Hall"],
        "Third Floor": ["Library", "Dean's Office"]
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📍 Smart Campus Navigation</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        :root {
            --bg: #0f0f17;
            --card-bg: rgba(30, 30, 46, 0.7);
            --accent: #89b4fa;
            --text-main: #cdd6f4;
            --text-dim: #a6adc8;
        }

        body {
            margin: 0;
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        .sidebar {
            width: 350px;
            background: var(--card-bg);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255,255,255,0.1);
            padding: 30px;
            display: flex;
            flex-direction: column;
            z-index: 1000;
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent);
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .search-box {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 12px 15px;
            border-radius: 12px;
            color: #fff;
            width: 100%;
            box-sizing: border-box;
            margin-bottom: 20px;
            outline: none;
        }

        .nav-sections {
            flex: 1;
            overflow-y: auto;
        }

        .nav-section {
            margin-bottom: 25px;
        }

        .nav-section h3 {
            font-size: 14px;
            text-transform: uppercase;
            color: var(--accent);
            letter-spacing: 1px;
            margin-bottom: 15px;
        }

        .location-item {
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 5px;
            font-size: 15px;
        }

        .location-item:hover {
            background: rgba(137, 180, 250, 0.1);
            color: var(--accent);
        }

        .map-container {
            flex: 1;
            position: relative;
        }

        #map {
            width: 100%;
            height: 100%;
        }

        .floor-map {
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            backdrop-filter: blur(15px);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            width: 300px;
            display: none;
            z-index: 999;
        }

        .floor-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
            overflow-x: auto;
        }

        .floor-tab {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            cursor: pointer;
            background: rgba(255,255,255,0.05);
            white-space: nowrap;
        }

        .floor-tab.active {
            background: var(--accent);
            color: #11111b;
        }

        .back-btn {
            margin-top: 20px;
            text-decoration: none;
            color: var(--text-dim);
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
    </style>
</head>
<body>

    <div class="sidebar">
        <div class="logo">📍 Campus Nav</div>
        
        <input type="text" class="search-box" placeholder="Search for library, lab, office...">

        <div class="nav-sections">
            <div class="nav-section">
                <h3>Outdoor Locations</h3>
                {% for loc in locations['Outdoor'] %}
                <div class="location-item" onclick="showOutdoor('{{ loc }}')">🏛️ {{ loc }}</div>
                {% endfor %}
            </div>

            <div class="nav-section">
                <h3>Indoor (Academic Building)</h3>
                <div class="location-item" onclick="showIndoor()">🏢 View Indoor Floor Map</div>
            </div>
        </div>

        <a href="http://127.0.0.1:8080" class="back-btn">← Back to Dashboard</a>
    </div>

    <div class="map-container">
        <div id="map"></div>
        
        <div class="floor-map" id="indoorPanel">
            <h4 style="margin: 0 0 15px 0;">Indoor Navigation</h4>
            <div class="floor-tabs">
                <div class="floor-tab active" onclick="switchFloor('Ground Floor')">GF</div>
                <div class="floor-tab" onclick="switchFloor('First Floor')">1F</div>
                <div class="floor-tab" onclick="switchFloor('Second Floor')">2F</div>
                <div class="floor-tab" onclick="switchFloor('Third Floor')">3F</div>
            </div>
            <div id="floorContent">
                <!-- Floor content injected here -->
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Initialize Map (Centering on a generic campus coordinate)
        var map = L.map('map').setView([12.9716, 77.5946], 17);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);

        var markers = {};

        function showOutdoor(name) {
            document.getElementById('indoorPanel').style.display = 'none';
            // Randomly offset markers around center for demo
            var lat = 12.9716 + (Math.random() - 0.5) * 0.005;
            var lng = 77.5946 + (Math.random() - 0.5) * 0.005;
            
            if (markers[name]) map.removeLayer(markers[name]);
            
            markers[name] = L.marker([lat, lng]).addTo(map)
                .bindPopup('<b>' + name + '</b><br>Fastest route: 2 mins walk')
                .openPopup();
            
            map.flyTo([lat, lng], 18);
        }

        function showIndoor() {
            document.getElementById('indoorPanel').style.display = 'block';
            switchFloor('Ground Floor');
        }

        var campusData = {{ locations | tojson }};

        function switchFloor(floor) {
            // Update tabs
            document.querySelectorAll('.floor-tab').forEach(t => {
                t.classList.toggle('active', t.innerText.includes(floor[0]));
            });

            var rooms = campusData['Academic Building'][floor];
            var html = '<ul style="list-style: none; padding: 0; margin: 0;">';
            rooms.forEach(r => {
                html += `<li style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px;">📍 ${r}</li>`;
            });
            html += '</ul>';
            document.getElementById('floorContent').innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, locations=CAMPUS_LOCATIONS)

if __name__ == '__main__':
    app.run(port=5003, debug=False)
