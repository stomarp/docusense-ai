"""
Section classifier integration (ML).

This module:
- Loads the trained scikit-learn model from ml/models/section_model.joblib
- Predicts section labels + confidence for text chunks
"""

from pathlib import Path
from typing import Optional, List, Dict, Tuple

import joblib


MODEL_PATH = Path("ml/models/section_model.joblib")


class SectionClassifier:
    """
    Wrapper around the scikit-learn pipeline so FastAPI can use it easily.
    """

    def __init__(self):
        self.model = None

    def load(self) -> None:
        """
        Load the trained model from disk.
        """
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found at {MODEL_PATH}. Train it first using: python ml/src/train.py"
            )
        self.model = joblib.load(MODEL_PATH)

    def is_ready(self) -> bool:
        return self.model is not None

    def predict_one(self, text: str) -> Tuple[str, float]:
        """
        Predict one label + confidence for a given text chunk.
        """
        probs = self.model.predict_proba([text])[0]
        classes = self.model.classes_

        best_idx = probs.argmax()
        return str(classes[best_idx]), float(probs[best_idx])

    def predict_many(self, chunks: List[str], min_chars: int = 40) -> List[Dict]:
        """
        Predict sections for multiple chunks and return structured results.

        min_chars: ignore very small chunks to reduce noise.
        """
        results = []

        for chunk in chunks:
            clean = chunk.strip()
            if len(clean) < min_chars:
                continue

            label, conf = self.predict_one(clean)

            results.append({
                "label": label,
                "confidence": round(conf, 4),
                "text_preview": clean[:160]
            })

        return results