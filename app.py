import os
import requests
from flask import Flask, request, jsonify, render_template

APP_TITLE = "Haritha Chat (Flask)"
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# -------------------------
# API key for testing only
# -------------------------
def get_api_key() -> str:
    """
    Return the hardcoded Gemini API key.
    ⚠️ Do NOT commit this key to public repos!
    """
    return "AIzaSyBGB7lHbfqCQqDBDiGnGJK_FigQQEidT1Q"


# -------------------------
# Flask app
# -------------------------
app = Flask(__name__)


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

    if not user_message:
        return jsonify({"error": "'message' is required"}), 400

    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": "Missing API key"}), 401

    # Convert chat history into Gemini contents format
    contents = []
    for msg in history:
        role = msg.get("role")
        txt = msg.get("content", "")
        if not txt:
            continue
        contents.append({
            "role": "user" if role == "user" else "model",
            "parts": [{"text": txt}]
        })
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are Haritha, a helpful Kerala farming assistant. "
                    "Be concise, practical, and Kerala-specific. "
                    "Prefer Malayalam greetings (Namaskaram) but keep main content in English. "
                    "Offer actionable steps and local crop examples (paddy, coconut, pepper, banana, rubber, spices). "
                    "Avoid hallucinations; admit if unsure."
                )
            }]
        },
        "contents": contents,
        "generationConfig": {"temperature": data.get("temperature", 0.7)}
    }

    url = f"{API_BASE}/models/{model}:generateContent?key={api_key}"

    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
    except requests.RequestException as e:
        return jsonify({"error": f"Network error: {e}"}), 502

    if not resp.ok:
        return jsonify({
            "error": f"API error {resp.status_code}",
            "details": resp.text
        }), resp.status_code

    try:
        data = resp.json()
    except ValueError:
        return jsonify({
            "error": "Invalid JSON from API",
            "details": resp.text[:2000]
        }), 502

    # Extract model reply
    candidates = data.get("candidates", [])
    text = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)

    return jsonify({
        "reply": text or "No content returned.",
        "raw": data  # include full response for debugging
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
