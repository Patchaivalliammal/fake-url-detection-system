
import os
import joblib

from flask import Flask, render_template, request, jsonify
from feature_extraction import extract_features


app = Flask(__name__)

# Model file location
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model",
    "phishing_model.pkl"
)

# Load trained model
model_data = None

if os.path.exists(MODEL_PATH):
    model_data = joblib.load(MODEL_PATH)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json(silent=True) or {}
        url = data.get("url", "").strip()

        if not url:
            return jsonify({
                "error": "Please enter a URL."
            }), 400

        if not model_data:
            return jsonify({
                "error": "Model is not available yet. Please train the model first."
            }), 503

        # Extract features
        features = extract_features(url)

        # Prepare model input
        model = model_data["model"]
        feature_names = model_data["feature_names"]

        import pandas as pd

        input_data = pd.DataFrame(
            [[features[name] for name in feature_names]],
            columns=feature_names
        )

        # Predict URL class
        prediction = int(model.predict(input_data)[0])

        # Get prediction confidence
        probabilities = model.predict_proba(input_data)[0]
        confidence = float(max(probabilities)) * 100

        if prediction == 1:
            result = "Phishing"
            message = "This URL has suspicious characteristics."
        else:
            result = "Legitimate"
            message = "The model did not detect suspicious patterns."

        return jsonify({
            "url": url,
            "prediction": result,
            "confidence": round(confidence, 2),
            "message": message
        })

    except Exception as error:
        app.logger.exception("Prediction failed")

        return jsonify({
            "error": "Unable to analyze this URL. Please check the input."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
