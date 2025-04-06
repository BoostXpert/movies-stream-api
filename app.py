from flask import Flask, request, jsonify, redirect
import jwt
import time
import os

app = Flask(__name__)

# Use a strong secret key
SECRET_KEY = "200000597866"

# Map obfuscated movie IDs to actual Google Drive file IDs
MOVIE_MAP = {
    "spiderman2021": "1AVRALg3PhoEzHuvSh29XhFwwLw4CfX8J",  # Replace with actual IDs
    "inception2010": "1XxYyZZabcdeFghijKlmNOPqrstu"
}

# Route to generate secure token and link
@app.route("/generate_token/<movie_id>")
def generate_token(movie_id):
    if movie_id not in MOVIE_MAP:
        return jsonify({"error": "Invalid movie"}), 404

    payload = {
        "movie_id": movie_id,
        "exp": int(time.time()) + 3600  # Token valid for 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    base_url = request.host_url.rstrip('/')
    return jsonify({
        "token": token,
        "secure_link": f"{base_url}/get_link/{movie_id}?token={token}"
    })

# Route to access the video via secure token
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
    gdrive_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return redirect(gdrive_url)

# Required by Render - don't indent this incorrectly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
