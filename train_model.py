
import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from feature_extraction import extract_features


# Dataset path
DATASET_PATH = "dataset/urls.csv"

# Model output path
MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "phishing_model.pkl")


def load_dataset():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            "Dataset not found. Please add dataset/urls.csv"
        )

    df = pd.read_csv(DATASET_PATH)

    if not {"url", "label"}.issubset(df.columns):
        raise ValueError(
            "Dataset must contain 'url' and 'label' columns."
        )

    df = df.dropna(subset=["url", "label"])
    df["url"] = df["url"].astype(str)

    # Convert labels to binary values
    label_map = {
        "legitimate": 0,
        "benign": 0,
        "safe": 0,
        "0": 0,
        "phishing": 1,
        "malicious": 1,
        "fake": 1,
        "1": 1
    }

    df["label"] = (
        df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(label_map)
    )

    df = df.dropna(subset=["label"])
    df["label"] = df["label"].astype(int)

    if df["label"].nunique() != 2:
        raise ValueError(
            "Dataset must contain both legitimate and phishing URLs."
        )

    return df


def train_model():

    print("Loading dataset...")

    df = load_dataset()

    print("Extracting URL features...")

    feature_rows = []

    for url in df["url"]:
        feature_rows.append(extract_features(url))

    X = pd.DataFrame(feature_rows)
    y = df["label"]

    print("Dataset size:", len(X))

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Training Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # Evaluate model
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\nModel Evaluation")
    print("----------------------")
    print("Accuracy:", round(accuracy * 100, 2), "%")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=["Legitimate", "Phishing"],
            zero_division=0
        )
    )

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    # Save trained model
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(
        {
            "model": model,
            "feature_names": list(X.columns)
        },
        MODEL_PATH
    )

    print("\nModel saved successfully!")
    print("Location:", MODEL_PATH)


if __name__ == "__main__":
    train_model()
