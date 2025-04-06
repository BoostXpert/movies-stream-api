from flask import Flask, request, jsonify, redirect
import jwt
import time
import os

app = Flask(__name__)

# Secret for signing tokens
SECRET_KEY = "20303929292"

# Your Google Drive API key
GOOGLE_API_KEY = "AIzaSyCKbHfoBx6YxBkXirXdUgUT7u8w5yYmzf0"  # <--- Replace with actual key

# Map movie IDs to actual Drive File IDs
MOVIE_MAP = {
    "spiderman2021": "1AVRALg3PhoEzHuvSh29XhFwwLw4CfX8J",  # Replace with actual Drive File IDs
    "inception2010": "1XxYyZZabcdeFghijKlmNOPqrstu"
}

# Route to generate tokenized link
@app.route("/generate_token/<movie_id>")
def generate_token(movie_id):
    if movie_id not in MOVIE_MAP:
        return jsonify({"error": "Invalid movie"}), 404

    payload = {
        "movie_id": movie_id,
        "exp": int(time.time()) + 3600  # 1 hour token
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    base_url = request.host_url.rstrip('/')
    return jsonify({
        "token": token,
        "secure_link": f"{base_url}/get_link/{movie_id}?token={token}"
    })

# Route to validate token and redirect to media
@app.route("/get_link/<movie_id>")
def get_link(movie_id):
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 401

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["movie_id"] != movie_id:
            return jsonify({"error": "Token mismatch"}), 403
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 403
    except Exception:
        return jsonify({"error": "Invalid token"}), 403

    file_id = MOVIE_MAP[movie_id]
    # Google Drive API media streaming URL
    drive_api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={GOOGLE_API_KEY}"

    return redirect(drive_api_url)

# Required for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
