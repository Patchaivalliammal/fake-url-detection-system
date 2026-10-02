
import os
import subprocess
import sys
import joblib

from flask import Flask, render_template, request, jsonify
from feature_extraction import extract_features


app = Flask(__name__)

MODEL_PATH = "model/phishing_model.pkl"

model_data = None


def load_model():

    global model_data

    if os.path.exists(MODEL_PATH):
        print("Loading existing model...")
        model_data = joblib.load(MODEL_PATH)

    else:
        print("Model not found. Starting training...")

        subprocess.run(
            [sys.executable, "train_model.py"],
            check=True
        )

        model_data = joblib.load(MODEL_PATH)

    print("Model loaded successfully!")


# Load or train model when application starts
load_model()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()

        if not data or "url" not in data:
            return jsonify({
                "error": "Please enter a URL."
            }), 400

        url = data["url"].strip()

        if not url:
            return jsonify({
                "error": "URL cannot be empty."
            }), 400

        # Extract URL features
        features = extract_features(url)

        # Arrange features in the same order used during training
        feature_names = model_data["feature_names"]

        input_data = [[
            features[name] for name in feature_names
        ]]

        model = model_data["model"]

        prediction = int(model.predict(input_data)[0])

        confidence = float(
            max(model.predict_proba(input_data)[0]) * 100
        )

        if prediction == 1:
            result = "Phishing"
            message = "Warning! This URL may be a phishing website."
        else:
            result = "Legitimate"
            message = "This URL appears legitimate."

        return jsonify({
            "url": url,
            "prediction": result,
            "confidence": round(confidence, 2),
            "message": message
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
