from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import numpy as np
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
MODEL_PATH = BASE_DIR / "model.pkl"

app = Flask(__name__, static_folder=str(FRONTEND_DIST), static_url_path="/")
CORS(app)

# ----------------------------
# Load ML model
# ----------------------------
with MODEL_PATH.open("rb") as model_file:
    model = pickle.load(model_file)

# ----------------------------
# Health Calculations
# ----------------------------

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def maintenance_calories(weight, height, age, gender, workout_days, workout_minutes):
    height_cm = height * 100
    bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + (5 if gender == 1 else -161)
    activity_boost = min((workout_days * workout_minutes) / 1500, 0.55)
    return bmr * (1.2 + activity_boost)

# ----------------------------
# Prediction API
# ----------------------------

@app.route("/predict", methods=["POST"])
@app.route("/api/predict", methods=["POST"])
def predict():

    data = request.json

    age = float(data["age"])
    gender = int(data["gender"])
    height = float(data["height"])
    weight = float(data["weight"])
    workout_days = float(data["workout_days"])
    workout_minutes = float(data["workout_minutes"])
    calories = float(data["calories"])
    protein = float(data["protein"])
    sleep = float(data["sleep"])
    goal_weight = float(data["goal_weight"])

    features = np.array([[age, gender, height, weight,
                          workout_days, workout_minutes,
                          calories, protein, sleep]])

    prediction = model.predict(features)[0]

    bmi = calculate_bmi(weight, height)
    maintenance = maintenance_calories(
        weight,
        height,
        age,
        gender,
        workout_days,
        workout_minutes
    )

    goal_progress = (prediction / goal_weight) * 100

    return jsonify({
        "predicted_weight": float(prediction),
        "bmi": round(bmi, 2),
        "maintenance_calories": round(maintenance, 2),
        "goal_progress": round(goal_progress, 2)
    })


# ----------------------------
# AI Fitness Chatbot
# ----------------------------

@app.route("/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.json
        message = data["message"]

        prompt = f"""
You are a professional fitness trainer.

Answer clearly and briefly.

User question: {message}
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()

        reply = result["response"]

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("Chat Error:", e)

        return jsonify({
            "reply": "AI trainer is unavailable. Make sure Ollama server is running."
        })


# ----------------------------
# Frontend Static Serving
# ----------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if FRONTEND_DIST.exists():
        target = FRONTEND_DIST / path
        if path and target.exists():
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify({"message": "Frontend build not found. Run `npm run build` in frontend."}), 404


# ----------------------------
# Run Server
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)
