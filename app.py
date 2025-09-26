import requests
from flask import Flask, request, jsonify, render_template

# -------------------------
# App Configuration
# -------------------------
APP_TITLE = "Haritha Chat (Flask)"
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.0-flash"

# Hardcoded APIs for testing
GEMINI_API_KEY = "AIzaSyBGB7lHbfqCQqDBDiGnGJK_FigQQEidT1Q"
VOICE_API_URL = "wss://stt-rt.soniox.com/transcribe-websocket"
VOICE_API_KEY = "f9c49e723255a24404d570c570f71470b23a715d03949924705e40ddc575b110"

# -------------------------
# Flask app
# -------------------------
app = Flask(__name__)

# -------------------------
# Helper Functions
# -------------------------
def get_api_key() -> str:
    """Return hardcoded Gemini API key."""
    return GEMINI_API_KEY

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return render_template("chat.html", title=APP_TITLE)


@app.route("/api/chat", methods=["POST"])
def api_chat():
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

    # System prompt
    if lang == "ml":
        system_text = (
            "നിങ്ങള്‍ ഹരിത (Haritha) എന്ന കേരള കര്‍ഷകര്‍ക്കായുള്ള സഹായിയാണ്. "
            "ഉപദേശങ്ങള്‍ ചുരുങ്ങിയ വാക്കുകളിലും വ്യക്തമായ ചുവടുവയ്പ്പുകളിലും മലയാളത്തിലായി നല്‍കുക. "
            "കേരളത്തിലെ കൃഷി പശ്ചാത്തലം, കാലാവസ്ഥ, ജലസേചനം, മണ്ണ് എന്നിവ പരിഗണിച്ച് പ്രായോഗിക നിര്‍ദ്ദേശങ്ങള്‍ നല്‍കുക. "
            "പ്രാദേശിക വിളങ്ങളുടെ (നെല്‍, തേങ്ങ, കുരുമുളക്, വാഴ, റബ്ബര്‍, മസാലകള്‍) ഉദാഹരണങ്ങള്‍ ഉള്‍പ്പെടുത്തുക. "
            "അറിയില്ലെങ്കില്‍ തുറന്നു സമ്മതിക്കുക; കല്‍പ്പനകള്‍ ഒഴിവാക്കുക."
        )
    else:
        system_text = (
            "You are Haritha, a helpful Kerala farming assistant. "
            "Be concise, practical, and Kerala-specific. "
            "Prefer Malayalam greetings (Namaskaram) but keep main content in English. "
            "Offer actionable steps and local crop examples (paddy, coconut, pepper, banana, rubber, spices). "
            "Avoid hallucinations; admit if unsure."
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

    return jsonify({
        "reply": text or "No content returned.",
        "raw": api_response
    })


@app.route("/api/transcribe", methods=["POST"])
def api_transcribe():
    """
    Proxies audio to Soniox Speech-to-Text API.
    Accepts multipart audio or raw body.
    """
    lang = (request.args.get("lang") or request.form.get("lang") or "en").lower()
    headers = {"Authorization": f"Bearer {VOICE_API_KEY}"}
    data = {"lang": lang}

    try:
        if "audio" in request.files:
            audio_file = request.files["audio"]
            files = {"audio": (audio_file.filename or "audio.webm", audio_file.stream,
                               audio_file.mimetype or "application/octet-stream")}
            resp = requests.post(VOICE_API_URL, data=data, files=files, headers=headers, timeout=60)
        else:
            raw = request.get_data()
            forward_headers = {**headers, "Content-Type": request.headers.get("Content-Type", "application/octet-stream")}
            resp = requests.post(f"{VOICE_API_URL}?lang={lang}", data=raw, headers=forward_headers, timeout=60)
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {e}"}), 502

    if not resp.ok:
        return jsonify({"error": f"API error {resp.status_code}", "details": resp.text}), resp.status_code

    try:
        j = resp.json()
    except ValueError:
        return jsonify({"transcript": resp.text})

    transcript = j.get("transcript") or j.get("text") or j.get("result") or (j if isinstance(j, str) else "")
    return jsonify({"transcript": transcript, "raw": j})


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    port = 5000
    app.run(host="0.0.0.0", port=port, debug=False)
