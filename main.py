 import os
import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for

app = Flask(__name__)

# 🔒 SET YOUR SECURITY CREDENTIALS HERE
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ABLcargo2026"

# Secret key required to keep your login sessions safe and unhackable
app.secret_key = "super_secret_secure_key_for_abl"
DB_FILE = "/tmp/cargo_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shipments (
            tracking_id TEXT PRIMARY KEY, status TEXT, origin TEXT, destination TEXT, current_location TEXT, weight TEXT, est_delivery TEXT
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM shipments")
    if cursor.fetchone() == 0:
        cursor.execute("INSERT INTO shipments VALUES ('CRG-998822', 'In Transit', 'Lagos Port, NG', 'Houston, USA', 'En Route via Ocean Freight', '1,240 kg', '15th June 2026')")
    conn.commit()
    conn.close()

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Cargo Express Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 15px; }
        .card { max-width: 500px; background: #ffffff; margin: 30px auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); text-align: center; }
        h1 { color: #1A0066; margin: 0 0 5px 0; font-size: 26px; }
        .tagline { color: #6b7280; font-size: 14px; margin-bottom: 25px; }
        label { display: block; text-align: left; font-weight: bold; margin-top: 12px; color: #374151; font-size: 14px;}
        input[type="text"], input[type="password"], select { width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 15px; outline: none; box-sizing: border-box; margin-top: 5px;}
        button { background-color: #FF6600; color: white; border: none; padding: 14px; width: 100%; font-size: 16px; font-weight: bold; border-radius: 8px; margin-top: 20px; cursor: pointer; }
        button.admin-btn { background-color: #1A0066; margin-top: 10px; }
        .result { text-align: left; background: #f9fafb; border: 1px solid #e5e7eb; border-left: 5px solid #1A0066; padding: 15px; margin-top: 25px; border-radius: 6px; }
        .badge { background: #1A0066; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .error { color: #dc2626; font-weight: bold; margin-top: 20px; font-size: 14px; }
        .success { color: #16a34a; font-weight: bold; margin-top: 20px; font-size: 14px; }
        .nav-link { display: inline-block; margin-top: 20px; color: #1A0066; text-decoration: none; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
    {% if page == 'track' %}
    <div class="card">
        <h1>🌐 CargoTrack</h1>
        <div class="tagline">Global Cargo & Logistics Tracking Portal</div>
        <form method="POST" action="/">
            <input type="text" name="track_id" placeholder="Enter Cargo ID (e.g. CRG-998822)" value="{{ typed_id }}" required>
            <button type="submit">TRACK SHIPMENT</button>
        </form>
        {% if data %}
            <div class="result">
                <h3>Shipment Details</h3>
                <p><b>Tracking Status:</b> <span class="badge">{{ data }}</span></p>
                <p><b>Current Location:</b> <span style="color: #FF6600; font-weight:bold;">📍 {{ data }}</span></p>
                <p><b>Route Journey:</b> {{ data }} ➡️ {{ data }}</p>
                <p><b>Cargo Weight:</b> {{ data }}</p>
                <p><b>Est. Delivery:</b> {{ data }}</p>
            </div>
        {% elif error %}
            <p class="error">❌ {{ error }}</p>
        {% endif %}
        <br>
        <a href="/admin" class="nav-link">Staff Login (Update Location) →</a>
    </div>
    {% endif %}

    {% if page == 'login' %}
    <div class="card" style="text-align: left;">
        <h2 style="color: #1A0066; text-align: center; margin:0;">🔒 Staff Authorization</h2>
        <div class="tagline text-center" style="margin-bottom:15px;">Please verify your identity</div>
        {% if error %}<p class="error">❌ {{ error }}</p>{% endif %}
        <form method="POST" action="/login">
            <label>Username:</label>
            <input type="text" name="username" required>
            <label>Password:</label>
            <input type="password" name="password" required>
            <button type="submit">LOG IN</button>
        </form>
    </div>
    {% endif %}

    {% if page == 'admin' %}
    <div class="card" style="text-align: left;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="color: #1A0066; margin:0;">👨‍💻 Manager Panel</h2>
            <a href="/logout" style="color: red; text-decoration: none; font-weight: bold; font-size:14px;">Logout</a>
        </div>
        {% if msg %}<p class="success">✅ {{ msg }}</p>{% endif %}
        <form method="POST" action="/admin">
            <label>Cargo Tracking ID:</label>
            <input type="text" name="tracking_id" placeholder="e.g. CRG-112233" required>
            <label>Current Status:</label>
            <select name="status">
                <option value="Manifest Picked Up">Manifest Picked Up</option>
                <option value="In Transit">In Transit</option>
                <option value="Customs Clearing Office">Customs Clearing Office</option>
                <option value="Out for Delivery">Out for Delivery</option>
                <option value="Delivered Successfully">Delivered Successfully</option>
            </select>
            <label>Current Location:</label>
            <input type="text" name="current_location" placeholder="e.g. Heathrow Hub, UK" required>
            <label>Origin:</label>
            <input type="text" name="origin" placeholder="e.g. Guangzhou, China" required>
            <label>Destination:</label>
            <input type="text" name="destination" placeholder="e.g. Lagos, Nigeria" required>
            <label>Package Weight:</label>
            <input type="text" name="weight" placeholder="e.g. 15.4 kg" required>
            <label>Estimated Arrival Date:</label>
            <input type="text" name="est_delivery" placeholder="e.g. 12th June 2026" required>
            <button type="submit" class="admin-btn">SAVE / UPDATE CARGO LOG</button>
        </form>
        <div style="text-align: center;"><a href="/" class="nav-link">← Go Back to Tracking Screen</a></div>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def track_home():
    data = None
    error = None
    typed_id = ""
    if request.method == "POST":
        typed_id = request.form.get("track_id", "").strip().upper()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shipments WHERE tracking_id=?", (typed_id,))
        data = cursor.fetchone()
        conn.close()
        if not data:
            error = "Tracking number not found in system."
    return render_template_string(HTML_LAYOUT, page='track', data=data, error=error, typed_id=typed_id)

@app.route("/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            error = "Invalid Username or Password."
    return render_template_string(HTML_LAYOUT, page='login', error=error)

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
        
    msg = None
    if request.method == "POST":
        t_id = request.form.get("tracking_id", "").strip().upper()
        status = request.form.get("status")
        loc = request.form.get("current_location", "").strip()
        org = request.form.get("origin", "").strip()
        dest = request.form.get("destination", "").strip()
        weight = request.form.get("weight", "").strip()
        delivery = request.form.get("est_delivery", "").strip()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shipments (tracking_id, status, origin, destination, current_location, weight, est_delivery)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tracking_id) DO UPDATE SET
                status=excluded.status, current_location=excluded.current_location,
                origin=excluded.origin, destination=excluded.destination,
                weight=excluded.weight, est_delivery=excluded.est_delivery
        ''', (t_id, status, org, dest, loc, weight, delivery))
        conn.commit()
        conn.close()
        msg = f"Cargo {t_id} updated successfully!"
    return render_template_string(HTML_LAYOUT, page='admin', msg=msg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('track_home'))

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
