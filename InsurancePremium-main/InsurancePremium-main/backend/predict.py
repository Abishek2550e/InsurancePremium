"""
predict.py
-----------
Loads the trained model pipeline and exposes a small, reusable API for
making single-record predictions. Used by main.py (FastAPI).
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from utils.preprocessing import ALL_FEATURES, compute_bmi, validate_input

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "premium_model.pkl"
METRICS_PATH = BASE_DIR / "model" / "metrics.json"


class PremiumPredictionError(Exception):
    """Raised when prediction fails due to invalid input or a missing model."""


class PremiumPredictor:
    """
    Wraps the trained sklearn pipeline (preprocessing + regressor) and
    provides a convenience method for single-record predictions.
    """

    def __init__(self, model_path: Path = MODEL_PATH, metrics_path: Path = METRICS_PATH):
        self.model_path = model_path
        self.metrics_path = metrics_path
        self.pipeline = None
        self.metrics = None
        self._load()

    def _load(self):
        if not self.model_path.exists():
            raise PremiumPredictionError(
                "Trained model not found. Please run 'python train_model.py' first."
            )
        try:
            self.pipeline = joblib.load(self.model_path)
        except Exception as exc:
            raise PremiumPredictionError(f"Failed to load model: {exc}") from exc

        if self.metrics_path.exists():
            with open(self.metrics_path) as f:
                self.metrics = json.load(f)

    @property
    def is_ready(self) -> bool:
        return self.pipeline is not None

    @property
    def r2_score(self) -> float:
        if self.metrics:
            return self.metrics["best_metrics"]["r2"]
        return float("nan")

    @property
    def model_name(self) -> str:
        if self.metrics:
            return self.metrics["best_model"]
        return "Unknown"

    def _prepare_record(self, record: dict) -> dict:
        record = dict(record)
        if record.get("bmi") in (None, 0) and record.get("height") and record.get("weight"):
            record["bmi"] = compute_bmi(record["height"], record["weight"])
        return record

    def predict_one(self, record: dict) -> dict:
        """
        Predict the premium for a single applicant.
        Returns a dict with the predicted premium and a confidence score
        derived from the model's R2 score on the held-out test set.
        """
        record = self._prepare_record(record)
        errors = validate_input(record)
        if errors:
            raise PremiumPredictionError("; ".join(errors))

        df = pd.DataFrame([record])[ALL_FEATURES]
        prediction = float(self.pipeline.predict(df)[0])
        confidence = max(0.0, min(1.0, self.r2_score)) * 100

        return {
            "predicted_premium": round(prediction, 2),
            "confidence": round(confidence, 1),
            "model_used": self.model_name,
        }

if __name__ == "__main__":
    predictor = PremiumPredictor()
    sample = {
        "age": 35,
        "gender": "male",
        "height": 175,
        "weight": 80,
        "smoker": "no",
        "children": 2,
        "region": "northeast",
    }
    print(predictor.predict_one(sample))
