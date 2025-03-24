import sqlite3
import secrets
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure random secret key

API_KEY = "7a6cfb01825070bd088b1eb5518fbb74"  # Replace with your OpenWeatherMap API key

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/get_pollution", methods=["POST"])
def get_pollution():
    if "username" not in session:
        return jsonify({"error": "Unauthorized access. Please log in."})

    data = request.json
    city = data.get("city")

    # Get city coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url)

    if geo_response.status_code != 200 or not geo_response.json():
        return jsonify({"error": "Could not retrieve location data"})

    location_data = geo_response.json()[0]
    lat, lon = location_data["lat"], location_data["lon"]

    # Get pollution data
    pollution_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    pollution_response = requests.get(pollution_url)

    if pollution_response.status_code != 200:
        return jsonify({"error": "Could not retrieve pollution data"})

    pollution_data = pollution_response.json()
    components = pollution_data["list"][0]["components"]
    air_quality_index = pollution_data["list"][0]["main"]["aqi"]

    pollution_levels = {
        1: {"status": "Good", "color": "green", "safe": "Yes"},
        2: {"status": "Fair", "color": "yellow", "safe": "Yes"},
        3: {"status": "Moderate", "color": "orange", "safe": "Caution"},
        4: {"status": "Poor", "color": "red", "safe": "No"},
        5: {"status": "Very Poor", "color": "purple", "safe": "No"},
    }

    result = {
        "city": city,
        "lat": lat,
        "lon": lon,
        "air_quality_index": air_quality_index,
        "pollution_status": pollution_levels[air_quality_index]["status"],
        "color": pollution_levels[air_quality_index]["color"],
        "safe_to_visit": pollution_levels[air_quality_index]["safe"],
        "components": components,
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
