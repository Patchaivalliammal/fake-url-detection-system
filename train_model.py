
import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from feature_extraction import extract_features


# Dataset path
DATASET_PATH = "dataset/urls.csv"

# Model save path
MODEL_PATH = "model/phishing_model.pkl"


def train_model():

    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    df = df.dropna(subset=["url", "label"])
    df = df.drop_duplicates(subset=["url"])

    print("Total URLs:", len(df))

    # Extract features
    print("Extracting features...")

    X = df["url"].apply(extract_features)

    X = pd.DataFrame(X.tolist())

    y = df["label"].astype(int)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Train model
    print("Training Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42
    )

    model.fit(X_train, y_train)

    # Evaluate model
    predictions = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, predictions))

    print(classification_report(y_test, predictions))

    # Create model folder automatically
    os.makedirs("model", exist_ok=True)

    # Save model and feature names
    model_data = {
        "model": model,
        "feature_names": list(X.columns)
    }

    joblib.dump(model_data, MODEL_PATH)

    print("Model saved successfully:", MODEL_PATH)


if __name__ == "__main__":
    train_model()
