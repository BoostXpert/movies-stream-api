from flask import Flask, request, jsonify, redirect
import jwt, time

app = Flask(__name__)
SECRET_KEY = "294983839"

# Map of obfuscated movie IDs to actual Google Drive file IDs
MOVIE_MAP = {
    "spiderman2021": "1AbC2DeFGhIjKlmNOPqRsTuVWXYZ",
    "inception2010": "1XxYyZZabcdeFghijKlmNOPqrstu"
}

# Generate signed token for movie
@app.route("/generate_token/<movie_id>")
def generate_token(movie_id):
    if movie_id not in MOVIE_MAP:
        return jsonify({"error": "Invalid movie"}), 404
    
    payload = {
        "movie_id": movie_id,
        "exp": int(time.time()) + 3600  # Expires in 1 hour
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({
        "token": token,
        "link": f"{request.host_url}get_link/{movie_id}?token={token}"
    })

# Validate token and redirect to movie
@app.route("/get_link/<movie_id>")
def get_link(movie_id):
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 401
    
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if data["movie_id"] != movie_id:
            return jsonify({"error": "Invalid movie"}), 403
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Link expired"}), 403
    except Exception as e:
        return jsonify({"error": "Invalid token"}), 403

    drive_id = MOVIE_MAP.get(movie_id)
    return redirect(f"https://drive.google.com/uc?export=download&id={drive_id}")