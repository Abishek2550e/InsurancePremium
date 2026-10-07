"""
fetch_dataset.py
-----------------
Downloads the real "Medical Cost Personal Datasets" health insurance
dataset (the same data published on Kaggle as mirichoi0218/insurance,
originally distributed with Brett Lantz's book "Machine Learning with
R") and saves it as insurance.csv with column names matching the rest
of this project.

Source mirror (public, no auth required):
    https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv

Run: python fetch_dataset.py
"""

import urllib.request
from pathlib import Path

import pandas as pd

SOURCE_URL = "https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/master/insurance.csv"
OUTPUT_PATH = Path(__file__).resolve().parent / "insurance.csv"

# Rename the original dataset's columns to match this project's naming.
COLUMN_RENAME = {"sex": "gender", "charges": "premium"}


def fetch_dataset() -> pd.DataFrame:
    with urllib.request.urlopen(SOURCE_URL) as response:
        df = pd.read_csv(response)

    df = df.rename(columns=COLUMN_RENAME)
    return df


if __name__ == "__main__":
    dataset = fetch_dataset()
    dataset.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset saved to: {OUTPUT_PATH} ({len(dataset)} rows)")
    print(dataset.head())
    print("\nMissing values per column:")
    print(dataset.isna().sum())
