"""
Preprocessing utilities shared between training and inference.

Keeping this logic in one place guarantees that the exact same feature
engineering is applied at train time and at prediction time.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

NUMERIC_FEATURES = ["age", "bmi", "children"]
CATEGORICAL_FEATURES = ["gender", "smoker", "region"]
TARGET = "premium"
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def compute_bmi(height_cm: float, weight_kg: float) -> float:
    """BMI = weight(kg) / height(m)^2."""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a raw insurance dataframe:
    - Standardize categorical text (lowercase, strip whitespace).
    - Recompute BMI if missing but height/weight are present.
    - Coerce numeric columns to numeric dtype.
    """
    df = df.copy()

    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "bmi" in df.columns and "height" in df.columns and "weight" in df.columns:
        missing_bmi = df["bmi"].isna() & df["height"].notna() & df["weight"].notna()
        df.loc[missing_bmi, "bmi"] = df.loc[missing_bmi].apply(
            lambda r: compute_bmi(r["height"], r["weight"]), axis=1
        )

    return df


def validate_input(record: dict) -> list[str]:
    """
    Validate a single user-submitted record.
    Returns a list of human-readable error messages (empty list = valid).
    """
    errors = []

    age = record.get("age")
    if age is None or not (18 <= age <= 100):
        errors.append("Age must be between 18 and 100 years.")

    height = record.get("height")
    if height is None or not (50 <= height <= 250):
        errors.append("Height must be between 50 and 250 cm.")

    weight = record.get("weight")
    if weight is None or not (10 <= weight <= 300):
        errors.append("Weight must be between 10 and 300 kg.")

    gender = record.get("gender")
    if gender not in ("male", "female"):
        errors.append("Gender must be 'male' or 'female'.")

    smoker = record.get("smoker")
    if smoker not in ("yes", "no"):
        errors.append("Smoker must be 'yes' or 'no'.")

    children = record.get("children")
    if children is None or not (0 <= children <= 10):
        errors.append("Number of children must be between 0 and 10.")

    region = record.get("region")
    if region not in ("northeast", "northwest", "southeast", "southwest"):
        errors.append("Region must be one of: northeast, northwest, southeast, southwest.")

    return errors
