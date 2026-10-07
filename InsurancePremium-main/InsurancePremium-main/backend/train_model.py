"""
train_model.py
---------------
Trains and compares multiple regression models for health insurance
premium prediction, selects the best performer, and persists it (along
with its preprocessing pipeline) to disk using joblib.

Models compared:
    - Linear Regression
    - Decision Tree Regressor
    - Random Forest Regressor

Run: python train_model.py
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from utils.preprocessing import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET,
    clean_dataframe,
)

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "insurance.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "premium_model.pkl"
METRICS_PATH = MODEL_DIR / "metrics.json"

RANDOM_STATE = 42


@dataclass
class ModelResult:
    name: str
    r2: float
    mae: float
    mse: float
    rmse: float
    train_seconds: float


def load_dataset(path: Path = DATASET_PATH) -> pd.DataFrame:
    """Load and clean the raw dataset: drop duplicate rows and rows with a missing target."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run dataset/fetch_dataset.py first."
        )
    df = pd.read_csv(path)
    df = clean_dataframe(df)

    duplicate_count = int(df.duplicated().sum())
    if duplicate_count:
        print(f"Found {duplicate_count} duplicate row(s) — removing.")
        df = df.drop_duplicates()

    df = df.dropna(subset=[TARGET])
    return df


def build_preprocessor() -> ColumnTransformer:
    """
    Build the sklearn ColumnTransformer that:
    - Imputes + scales numeric features.
    - Imputes + one-hot encodes categorical features.
    """
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )


def get_candidate_models() -> dict:
    return {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(
            max_depth=8, min_samples_leaf=5, random_state=RANDOM_STATE
        ),
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_leaf=3,
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }


def evaluate(y_true, y_pred) -> dict:
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_true, y_pred)
    return {"r2": r2, "mae": mae, "mse": mse, "rmse": rmse}


def train_and_compare(df: pd.DataFrame):
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    preprocessor = build_preprocessor()
    results: list[ModelResult] = []
    fitted_pipelines: dict[str, Pipeline] = {}

    for name, model in get_candidate_models().items():
        pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])

        start = time.time()
        pipeline.fit(X_train, y_train)
        elapsed = time.time() - start

        y_pred = pipeline.predict(X_test)
        metrics = evaluate(y_test, y_pred)

        results.append(
            ModelResult(
                name=name,
                r2=metrics["r2"],
                mae=metrics["mae"],
                mse=metrics["mse"],
                rmse=metrics["rmse"],
                train_seconds=elapsed,
            )
        )
        fitted_pipelines[name] = pipeline
        print(
            f"[{name}] R2={metrics['r2']:.4f}  MAE={metrics['mae']:.2f}  "
            f"MSE={metrics['mse']:.2f}  RMSE={metrics['rmse']:.2f}  "
            f"({elapsed:.2f}s)"
        )

    best = max(results, key=lambda r: r.r2)
    best_pipeline = fitted_pipelines[best.name]
    print(f"\nBest model: {best.name} (R2={best.r2:.4f})")

    return best, best_pipeline, results


def save_artifacts(best: ModelResult, pipeline: Pipeline, all_results: list[ModelResult]):
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    metrics_payload = {
        "best_model": best.name,
        "best_metrics": asdict(best),
        "all_results": [asdict(r) for r in all_results],
        "feature_columns": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\nModel saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


def main():
    print("Loading dataset...")
    df = load_dataset()
    print(f"Loaded {len(df)} rows after cleaning.\n")

    print("Training and comparing models...\n")
    best, best_pipeline, all_results = train_and_compare(df)

    save_artifacts(best, best_pipeline, all_results)


if __name__ == "__main__":
    main()
