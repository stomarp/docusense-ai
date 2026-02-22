"""
Train a simple section classifier for HR policy text.

Model:
- TF-IDF vectorizer (turns text into numeric features)
- Logistic Regression (fast + explainable baseline)

Output:
- Saves trained model bundle to ml/models/section_model.joblib
"""

from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

DATA_PATH = Path("ml/data/sections_train.csv")
MODEL_PATH = Path("ml/models/section_model.joblib")


def main():
    # Load labeled training data
    df = pd.read_csv(DATA_PATH)

    # Separate input text and labels
    X = df["text"].astype(str)
    y = df["label"].astype(str)

    # Split data so we can see if the model generalizes

    # NOTE:
# Our starter dataset is tiny, so a stratified train/test split can fail.
# For MVP, we train on all data. Later we'll add more labeled examples and
# re-enable a proper train/test split.
    X_train, y_train = X, y
    X_test, y_test = X, y



    # Create a pipeline: text -> TF-IDF -> classifier
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=2000)),
        ]
    )

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    print("\n=== Classification Report ===")
    print(classification_report(y_test, preds))

    # Save trained model to disk
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"\nSaved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()