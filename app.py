from flask import Flask, request, jsonify
import jwt
import time
import os

app = Flask(__name__)

SECRET_KEY = "20303929292"

MOVIE_MAP = {
    "spiderman2021": "1AVRALg3PhoEzHuvSh29XhFwwLw4CfX8J",
    "inception2010": "1XxYyZZabcdeFghijKlmNOPqrstu"
}

@app.route("/generate_token/<movie_id>")
def generate_token(movie_id):
    if movie_id not in MOVIE_MAP:
        return jsonify({"error": "Invalid movie"}), 404

    payload = {
        "movie_id": movie_id,
        "exp": int(time.time()) + 3600
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return jsonify({
        "token": token,
        "secure_link": f"https://cinetalk.aman221.workers.dev/proxy/{movie_id}?token={token}"
    })

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

    file_id = MOVIE_MAP.get(movie_id)
    return jsonify({"drive_id": file_id})

# Required for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
