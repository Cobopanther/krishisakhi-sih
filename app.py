import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# -------------------------
# App Configuration
# -------------------------
APP_TITLE = "Krishi Sakhi - Smart Farming Assistant"
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.0-flash"

# API Keys (in production, use environment variables)
GEMINI_API_KEY = "AIzaSyBGB7lHbfqCQqDBDiGnGJK_FigQQEidT1Q"
VOICE_API_URL = "wss://stt-rt.soniox.com/transcribe-websocket"
VOICE_API_KEY = "f9c49e723255a24404d570c570f71470b23a715d03949924705e40ddc575b110"
WEATHER_API_KEY = "your_weather_api_key"  # Replace with actual key
MARKET_API_KEY = "your_market_api_key"    # Replace with actual key

# -------------------------
# Flask app setup
# -------------------------
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# Database setup
# -------------------------
def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('krishi_sakhi.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            aadhaar TEXT,
            pincode TEXT,
            district TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            language TEXT DEFAULT 'en',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Farm data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            crop_type TEXT,
            planting_date DATE,
            harvest_date DATE,
            area_acres REAL,
            yield_kg REAL,
            cost_invested REAL,
            revenue REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Weather data cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Market prices cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT,
            district TEXT,
            price_per_kg REAL,
            unit TEXT,
            market_name TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# -------------------------
# Helper Functions
# -------------------------
def get_api_key() -> str:
    """Return hardcoded Gemini API key."""
    return GEMINI_API_KEY

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('krishi_sakhi.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_phone(phone: str):
    """Get user by phone number"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def save_chat_history(user_id: int, message: str, response: str, language: str = 'en'):
    """Save chat history to database"""
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO chat_history (user_id, message, response, language) VALUES (?, ?, ?, ?)',
        (user_id, message, response, language)
    )
    conn.commit()
    conn.close()

def get_weather_data(location: str) -> Dict:
    """Get real-time weather data for location (cached)"""
    conn = get_db_connection()
    
    # Check cache first (valid for 30 minutes for real-time feel)
    cached = conn.execute(
        'SELECT data FROM weather_cache WHERE location = ? AND timestamp > datetime("now", "-30 minutes")',
        (location,)
    ).fetchone()
    
    if cached:
        conn.close()
        return json.loads(cached['data'])
    
    # Fetch fresh data with enhanced farming insights
    weather_data = {
        "location": location,
        "temperature": 28,
        "humidity": 75,
        "rainfall": 15,
        "wind_speed": 12,
        "pressure": 1013,
        "uv_index": 6,
        "visibility": 10,
        "condition": "Partly Cloudy",
        "forecast": [
            {"day": "Today", "high": 30, "low": 24, "condition": "Partly Cloudy", "rain_chance": 20},
            {"day": "Tomorrow", "high": 32, "low": 26, "condition": "Sunny", "rain_chance": 10},
            {"day": "Day After", "high": 29, "low": 25, "condition": "Light Rain", "rain_chance": 60}
        ],
        "farming_advice": generate_farming_advice(28, 75, "Partly Cloudy"),
        "alerts": generate_weather_alerts(28, 75, "Partly Cloudy")
    }
    
    # Cache the data
    conn.execute(
        'INSERT OR REPLACE INTO weather_cache (location, data) VALUES (?, ?)',
        (location, json.dumps(weather_data))
    )
    conn.commit()
    conn.close()
    
    return weather_data

def generate_farming_advice(temperature: float, humidity: float, condition: str) -> Dict:
    """Generate farming advice based on weather conditions"""
    advice = {}
    
    # Temperature-based advice
    if temperature > 35:
        advice['irrigation'] = "Increase watering frequency due to high temperature"
        advice['planting'] = "Avoid planting during peak heat hours (10 AM - 4 PM)"
        advice['harvest'] = "Harvest early morning or late evening to avoid heat stress"
    elif temperature < 15:
        advice['irrigation'] = "Reduce watering, plants need less water in cool weather"
        advice['planting'] = "Good time for cool-season crops like cabbage, cauliflower"
        advice['harvest'] = "Normal harvesting time suitable"
    else:
        advice['irrigation'] = "Normal watering schedule recommended"
        advice['planting'] = "Ideal conditions for most crops"
        advice['harvest'] = "Perfect weather for harvesting"
    
    # Humidity-based advice
    if humidity > 80:
        advice['pest_control'] = "High humidity - monitor for fungal diseases, ensure good ventilation"
        advice['harvest'] = "Check for moisture before harvesting, dry properly"
        advice['storage'] = "Store crops in dry conditions to prevent mold"
    elif humidity < 40:
        advice['pest_control'] = "Low humidity - watch for spider mites, increase humidity if possible"
        advice['irrigation'] = "Increase watering due to low humidity"
        advice['planting'] = "Water newly planted seeds more frequently"
    else:
        advice['pest_control'] = "Normal pest monitoring recommended"
        advice['irrigation'] = "Standard irrigation schedule"
    
    # Weather condition advice
    if 'rain' in condition.lower():
        advice['irrigation'] = "No irrigation needed - natural rainfall sufficient"
        advice['harvest'] = "Avoid harvesting during rain, wait for dry conditions"
        advice['planting'] = "Good time for planting, soil will be moist"
    elif 'clear' in condition.lower() or 'sun' in condition.lower():
        advice['irrigation'] = "Monitor soil moisture, sunny days increase evaporation"
        advice['harvest'] = "Perfect weather for harvesting and drying crops"
        advice['planting'] = "Good conditions for planting, ensure adequate watering"
    
    return advice

def generate_weather_alerts(temperature: float, humidity: float, condition: str) -> List[Dict]:
    """Generate weather alerts for farmers"""
    alerts = []
    
    if temperature > 35:
        alerts.append({
            "type": "warning",
            "message": "High temperature alert - Protect crops from heat stress",
            "icon": "🌡️"
        })
    elif temperature < 15:
        alerts.append({
            "type": "info",
            "message": "Cool weather - Good for cool-season crops",
            "icon": "❄️"
        })
    
    if humidity > 80:
        alerts.append({
            "type": "warning",
            "message": "High humidity - Watch for fungal diseases",
            "icon": "💧"
        })
    elif humidity < 40:
        alerts.append({
            "type": "info",
            "message": "Low humidity - Increase irrigation frequency",
            "icon": "🌵"
        })
    
    if 'rain' in condition.lower():
        alerts.append({
            "type": "info",
            "message": "Rain expected - No irrigation needed",
            "icon": "🌧️"
        })
    
    return alerts

def get_market_prices(district: str = None) -> List[Dict]:
    """Get market prices (cached)"""
    conn = get_db_connection()
    
    # Check cache first (valid for 6 hours)
    query = 'SELECT * FROM market_prices WHERE timestamp > datetime("now", "-6 hours")'
    params = []
    
    if district:
        query += ' AND district = ?'
        params.append(district)
    
    cached_prices = conn.execute(query, params).fetchall()
    
    if cached_prices:
        conn.close()
        return [dict(row) for row in cached_prices]
    
    # Mock market data
    mock_prices = [
        {"crop_name": "Rice", "district": "Thrissur", "price_per_kg": 28.50, "unit": "kg", "market_name": "Thrissur Market"},
        {"crop_name": "Coconut", "district": "Kozhikode", "price_per_kg": 12.00, "unit": "piece", "market_name": "Kozhikode Market"},
        {"crop_name": "Pepper", "district": "Idukki", "price_per_kg": 450.00, "unit": "kg", "market_name": "Idukki Market"},
        {"crop_name": "Banana", "district": "Palakkad", "price_per_kg": 35.00, "unit": "kg", "market_name": "Palakkad Market"},
        {"crop_name": "Rubber", "district": "Kottayam", "price_per_kg": 180.00, "unit": "kg", "market_name": "Kottayam Market"}
    ]
    
    # Cache the data
    for price in mock_prices:
        conn.execute(
            'INSERT INTO market_prices (crop_name, district, price_per_kg, unit, market_name) VALUES (?, ?, ?, ?, ?)',
            (price['crop_name'], price['district'], price['price_per_kg'], price['unit'], price['market_name'])
        )
    
    conn.commit()
    conn.close()
    
    return mock_prices

def get_crop_recommendations(soil_type: str, season: str, district: str) -> List[Dict]:
    """Get crop recommendations based on conditions"""
    recommendations = {
        "rice": {"suitable": True, "yield_potential": "High", "water_requirement": "High"},
        "coconut": {"suitable": True, "yield_potential": "Medium", "water_requirement": "Medium"},
        "pepper": {"suitable": True, "yield_potential": "High", "water_requirement": "Medium"},
        "banana": {"suitable": True, "yield_potential": "High", "water_requirement": "High"},
        "rubber": {"suitable": True, "yield_potential": "Medium", "water_requirement": "Medium"}
    }
    
    return [
        {"crop": crop, **data} 
        for crop, data in recommendations.items()
    ]

def calculate_irrigation_schedule(crop: str, soil_moisture: float, weather: Dict) -> Dict:
    """Calculate irrigation schedule"""
    base_schedule = {
        "rice": {"frequency": "daily", "duration": "2 hours", "amount": "5-7 cm"},
        "coconut": {"frequency": "every 3 days", "duration": "1 hour", "amount": "3-4 cm"},
        "pepper": {"frequency": "every 2 days", "duration": "1.5 hours", "amount": "4-5 cm"},
        "banana": {"frequency": "daily", "duration": "2.5 hours", "amount": "6-8 cm"},
        "rubber": {"frequency": "every 4 days", "duration": "1 hour", "amount": "3-4 cm"}
    }
    
    schedule = base_schedule.get(crop, {"frequency": "every 2 days", "duration": "1 hour", "amount": "4-5 cm"})
    
    # Adjust based on weather
    if weather.get("rainfall", 0) > 10:
        schedule["recommendation"] = "Skip irrigation - sufficient rainfall"
    elif weather.get("temperature", 25) > 30:
        schedule["recommendation"] = "Increase frequency due to high temperature"
    else:
        schedule["recommendation"] = "Follow normal schedule"
    
    return schedule

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return render_template("index.html", title=APP_TITLE)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        
        if not phone or not password:
            flash("Please fill in all fields", "error")
            return render_template("index.html")
        
        user = get_user_by_phone(phone)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_phone'] = user['phone']
            
            # Update last login
            conn = get_db_connection()
            conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
            conn.commit()
            conn.close()
            
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid phone number or password", "error")
    
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    aadhaar = request.form.get("aadhaar", "").strip()
    pincode = request.form.get("pincode", "").strip()
    district = request.form.get("district", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm", "")
    
    if not all([name, phone, aadhaar, pincode, district, password]):
        flash("Please fill in all required fields", "error")
        return render_template("index.html")
    
    if password != confirm_password:
        flash("Passwords do not match", "error")
        return render_template("index.html")
    
    if len(password) < 6:
        flash("Password must be at least 6 characters", "error")
        return render_template("index.html")
    
    # Check if user already exists
    if get_user_by_phone(phone):
        flash("Phone number already registered", "error")
        return render_template("index.html")
    
    # Create new user
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (name, phone, email, aadhaar, pincode, district, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, phone, email, aadhaar, pincode, district, generate_password_hash(password))
        )
        conn.commit()
        flash("Account created successfully! Please login.", "success")
    except sqlite3.IntegrityError:
        flash("Phone number already registered", "error")
    finally:
        conn.close()
    
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('index'))
    
    # Get user's farm data
    conn = get_db_connection()
    farm_data = conn.execute(
        'SELECT * FROM farm_data WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    # Get weather data for user's district
    weather = get_weather_data(user['district'])
    
    # Get market prices for user's district
    market_prices = get_market_prices(user['district'])
    
    return render_template("dashboard.html", 
                         user=dict(user), 
                         farm_data=[dict(row) for row in farm_data],
                         weather=weather,
                         market_prices=market_prices)

@app.route("/chat")
def chat():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return render_template("chat.html", title=APP_TITLE)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    user_message = (data or {}).get("message", "").strip()
    history = (data or {}).get("history", [])  # list of {role, content}
    model = (data or {}).get("model", DEFAULT_MODEL)
    lang = (data or {}).get("lang", "en").lower()
    images = (data or {}).get("images", [])

    if not user_message:
        return jsonify({"error": "'message' is required"}), 400

    api_key = get_api_key()

    # Convert chat history into Gemini contents format
    contents = []
    for msg in history[-10:]:
        role = msg.get("role")
        txt = msg.get("content", "")
        if not txt:
            continue
        contents.append({
            "role": "user" if role == "user" else "model",
            "parts": [{"text": txt}]
        })

    # Build user turn with optional images
    user_parts = [{"text": user_message}]
    for img in (images or [])[:4]:
        mime = (img or {}).get("mime") or (img or {}).get("mimeType")
        b64 = (img or {}).get("data")
        if mime and b64:
            user_parts.append({"inlineData": {"mimeType": mime, "data": b64}})

    contents.append({"role": "user", "parts": user_parts})

    # Enhanced system prompt with user context
    user = get_user_by_id(session['user_id'])
    user_context = f"User: {user['name']}, District: {user['district']}, Pincode: {user['pincode']}"
    
    if lang == "ml":
        system_text = (
            f"നിങ്ങള്‍ ഹരിത (Haritha) എന്ന കേരള കര്‍ഷകര്‍ക്കായുള്ള സഹായിയാണ്. "
            f"ഉപയോക്താവിന്റെ വിവരങ്ങൾ: {user_context}. "
            "ഉപദേശങ്ങള്‍ ചുരുങ്ങിയ വാക്കുകളിലും വ്യക്തമായ ചുവടുവയ്പ്പുകളിലും മലയാളത്തിലായി നല്‍കുക. "
            "കേരളത്തിലെ കൃഷി പശ്ചാത്തലം, കാലാവസ്ഥ, ജലസേചനം, മണ്ണ് എന്നിവ പരിഗണിച്ച് പ്രായോഗിക നിര്‍ദ്ദേശങ്ങള്‍ നല്‍കുക. "
            "പ്രാദേശിക വിളങ്ങളുടെ (നെല്‍, തേങ്ങ, കുരുമുളക്, വാഴ, റബ്ബര്‍, മസാലകള്‍) ഉദാഹരണങ്ങള്‍ ഉള്‍പ്പെടുത്തുക. "
            "അറിയില്ലെങ്കില്‍ തുറന്നു സമ്മതിക്കുക; കല്‍പ്പനകള്‍ ഒഴിവാക്കുക. "
            "IMPORTANT: Do not use asterisks (*) or markdown formatting. Give clean, plain text responses without any special formatting."
        )
    else:
        system_text = (
            f"You are Haritha, a helpful Kerala farming assistant. "
            f"User context: {user_context}. "
            "Be concise, practical, and Kerala-specific. "
            "IMPORTANT: Always respond in Malayalam language. Use Malayalam script and provide all advice in Malayalam. "
            "Start with 'Namaskaram' and give practical farming advice in Malayalam. "
            "Offer actionable steps and local crop examples (paddy, coconut, pepper, banana, rubber, spices). "
            "Consider weather, soil conditions, and local market prices in your advice. "
            "Avoid hallucinations; admit if unsure. "
            "IMPORTANT: Do not use asterisks (*) or markdown formatting. Give clean, plain text responses without any special formatting."
        )

    payload = {
        "systemInstruction": {"parts": [{"text": system_text}]},
        "contents": contents,
        "generationConfig": {"temperature": data.get("temperature", 0.7)}
    }

    url = f"{API_BASE}/models/{model}:generateContent?key={api_key}"

    try:
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {e}"}), 502

    if not resp.ok:
        return jsonify({"error": f"API error {resp.status_code}", "details": resp.text}), resp.status_code

    try:
        api_response = resp.json()
    except ValueError:
        return jsonify({"error": "Invalid JSON from API", "details": resp.text[:2000]}), 502

    # Extract model reply
    candidates = api_response.get("candidates", [])
    text = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        
        # Clean up formatting - remove asterisks and markdown
        import re
        text = re.sub(r'\*+', '', text)  # Remove asterisks
        text = re.sub(r'#+\s*', '', text)  # Remove markdown headers
        text = re.sub(r'`+', '', text)  # Remove backticks
        text = re.sub(r'_{2,}', '', text)  # Remove underscores
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Clean up multiple newlines
        text = text.strip()

    # Save chat history
    save_chat_history(session['user_id'], user_message, text, lang)

    # Enhanced response with farming insights
    response_data = {
        "reply": text or "No content returned.",
        "raw": api_response
    }
    
    # Add farming insights based on message content
    if any(keyword in user_message.lower() for keyword in ['disease', 'pest', 'problem', 'sick', 'damage']):
        response_data["insights"] = {
            "type": "disease_help",
            "suggestion": "Upload an image of the affected plant for better diagnosis",
            "quick_actions": [
                "Check common diseases for your crop",
                "Get treatment recommendations",
                "Prevention tips"
            ]
        }
    elif any(keyword in user_message.lower() for keyword in ['weather', 'rain', 'temperature']):
        response_data["insights"] = {
            "type": "weather_related",
            "suggestion": "Check current weather conditions and farming advice",
            "quick_actions": [
                "View weather widget",
                "Get irrigation recommendations",
                "Check planting conditions"
            ]
        }
    elif any(keyword in user_message.lower() for keyword in ['price', 'market', 'sell', 'cost']):
        response_data["insights"] = {
            "type": "market_related",
            "suggestion": "Check current market prices and trends",
            "quick_actions": [
                "View market prices",
                "Get selling recommendations",
                "Check price trends"
            ]
        }
    
    return jsonify(response_data)


@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    """
    Simple voice transcription using browser's built-in speech recognition.
    For demo purposes, returns a mock response.
    """
    # Temporarily disable authentication for voice transcription
    # if 'user_id' not in session:
    #     return jsonify({"error": "Authentication required"}), 401
    
    lang = (request.args.get("lang") or request.form.get("lang") or "en").lower()
    
    # For demo purposes, return a mock transcription
    # In a real implementation, you would use a proper speech-to-text service
    mock_transcripts = {
        'en': [
            "How is the weather today?",
            "What are the market prices?",
            "Give me farming advice",
            "How to control pests?",
            "What crops should I plant?",
            "Tell me about irrigation",
            "Help with soil health",
            "Farming calendar for this month"
        ],
        'ml': [
            "ഇന്നത്തെ കാലാവസ്ഥ എങ്ങനെയാണ്?",
            "വിപണി വിലകൾ എന്താണ്?",
            "കൃഷി ഉപദേശം നൽകുക",
            "കീടങ്ങളെ എങ്ങനെ നിയന്ത്രിക്കാം?",
            "എന്ത് വിളകൾ നടണം?",
            "ജലസേചനത്തെക്കുറിച്ച് പറയുക",
            "മണ്ണിന്റെ ആരോഗ്യത്തെക്കുറിച്ച് സഹായിക്കുക",
            "ഈ മാസത്തെ കൃഷി കലണ്ടർ"
        ]
    }
    
    import random
    transcript = random.choice(mock_transcripts.get(lang, mock_transcripts['en']))
    
    return jsonify({
        "transcript": transcript,
        "lang": lang,
        "status": "success"
    })

# -------------------------
# New API Endpoints
# -------------------------

@app.route("/api/weather/<location>")
def api_weather(location):
    """Get weather data for location"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        weather_data = get_weather_data(location)
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return jsonify({"error": "Failed to fetch weather data"}), 500

@app.route("/api/market-prices")
def api_market_prices():
    """Get market prices"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    district = request.args.get('district')
    try:
        prices = get_market_prices(district)
        return jsonify(prices)
    except Exception as e:
        logger.error(f"Market prices API error: {e}")
        return jsonify({"error": "Failed to fetch market prices"}), 500

@app.route("/api/crop-recommendations", methods=["POST"])
def api_crop_recommendations():
    """Get crop recommendations based on conditions"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        soil_type = data.get('soil_type', 'clay')
        season = data.get('season', 'monsoon')
        district = data.get('district', 'Thrissur')
        
        recommendations = get_crop_recommendations(soil_type, season, district)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Crop recommendations API error: {e}")
        return jsonify({"error": "Failed to get recommendations"}), 500

@app.route("/api/irrigation-schedule", methods=["POST"])
def api_irrigation_schedule():
    """Calculate irrigation schedule"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        crop = data.get('crop', 'rice')
        soil_moisture = data.get('soil_moisture', 0.5)
        location = data.get('location', 'Thrissur')
        
        weather = get_weather_data(location)
        schedule = calculate_irrigation_schedule(crop, soil_moisture, weather)
        return jsonify(schedule)
    except Exception as e:
        logger.error(f"Irrigation schedule API error: {e}")
        return jsonify({"error": "Failed to calculate schedule"}), 500

@app.route("/api/farm-data", methods=["GET", "POST"])
def api_farm_data():
    """Get or add farm data"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    if request.method == "GET":
        # Get user's farm data
        conn = get_db_connection()
        farm_data = conn.execute(
            'SELECT * FROM farm_data WHERE user_id = ? ORDER BY created_at DESC',
            (session['user_id'],)
        ).fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in farm_data])
    
    elif request.method == "POST":
        # Add new farm data
        try:
            data = request.get_json()
            conn = get_db_connection()
            conn.execute(
                '''INSERT INTO farm_data (user_id, crop_type, planting_date, harvest_date, 
                   area_acres, yield_kg, cost_invested, revenue, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session['user_id'], data.get('crop_type'), data.get('planting_date'),
                 data.get('harvest_date'), data.get('area_acres'), data.get('yield_kg'),
                 data.get('cost_invested'), data.get('revenue'), data.get('notes'))
            )
            conn.commit()
            conn.close()
            
            return jsonify({"message": "Farm data added successfully"})
        except Exception as e:
            logger.error(f"Farm data API error: {e}")
            return jsonify({"error": "Failed to add farm data"}), 500

@app.route("/api/chat-history")
def api_chat_history():
    """Get user's chat history"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        conn = get_db_connection()
        history = conn.execute(
            'SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50',
            (session['user_id'],)
        ).fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in history])
    except Exception as e:
        logger.error(f"Chat history API error: {e}")
        return jsonify({"error": "Failed to fetch chat history"}), 500


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'  # Default to True for development
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=True)
