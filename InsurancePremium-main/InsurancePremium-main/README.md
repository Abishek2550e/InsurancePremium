# 🩺 Health Insurance Premium Prediction System

A machine learning web application that predicts an individual's annual
health insurance premium based on demographic and lifestyle factors —
built as a final-year Computer Science Engineering project.

No database is used; the app runs entirely on a trained ML model
persisted with **joblib** and a CSV dataset. The system is split into a
**FastAPI backend** (serves the model over a JSON API) and a **plain
HTML/CSS/JavaScript frontend** (consumes that API with the Fetch API —
no frameworks or build step required).

---

## 1. Problem Statement

Health insurance premiums are traditionally calculated by insurers using
opaque, manual actuarial rules. Applicants have little visibility into
*why* a premium is what it is, and insurers spend significant manual
effort on routine quoting. This project builds a transparent, data-driven
system that predicts premiums instantly from applicant attributes using
supervised machine learning.

## 2. Objectives

- Build a clean, reusable ML pipeline for premium prediction.
- Compare multiple regression algorithms and automatically select the
  best performer using standard regression metrics.
- Provide an interactive, modern web form for single-applicant premium
  prediction.
- Avoid any external database — the system is fully self-contained and
  portable.

## 3. Tech Stack

| Layer              | Technology                                  |
|--------------------|-----------------------------------------------|
| Backend language   | Python 3.x                                     |
| Backend framework  | FastAPI + Uvicorn                              |
| Frontend           | Plain HTML5, CSS3, vanilla JavaScript (ES6+)   |
| Frontend ↔ backend | Fetch API (JSON)                               |
| Data handling      | Pandas, NumPy                                  |
| Machine Learning   | scikit-learn                                   |
| Visualization      | Hand-rolled inline SVG gauge chart (no chart library) |
| Model persistence  | Joblib                                         |

No npm, no bundler, no framework — the frontend is a handful of static
`.html`, `.css`, and `.js` files that any static file server can host.

## 4. Dataset Description

This project trains on the **real "Medical Cost Personal Datasets"**
dataset — the same one published on Kaggle as
[`mirichoi0218/insurance`](https://www.kaggle.com/datasets/mirichoi0218/insurance),
originally distributed with Brett Lantz's book *"Machine Learning with
R"*. It contains **1,338 real (anonymized) U.S. health insurance
records** with no missing values.

`dataset/fetch_dataset.py` downloads it from a public mirror of the
same data (no Kaggle account/API key required) and saves it as
`dataset/insurance.csv`, renaming two columns (`sex` → `gender`,
`charges` → `premium`) to match this project's naming:

| Column   | Description                                        |
|----------|------------------------------------------------------|
| age      | Applicant age (years) — range 18–64 in the dataset     |
| gender   | male / female                                          |
| bmi      | Body Mass Index                                        |
| smoker   | yes / no                                               |
| children | Number of dependents                                   |
| region   | northeast / northwest / southeast / southwest (US)     |
| premium  | **Target** — annual medical insurance charges (USD)    |

The prediction form also asks for **height** and **weight** so BMI can
be calculated for the user automatically (`weight_kg / height_m²`) —
those two fields are not sent to the model as separate features, only
the resulting `bmi` is, since that's what the source dataset provides.

## 5. Data Preprocessing

Implemented in `utils/preprocessing.py` and `train_model.py`:

- Text normalization (lowercase, trimmed) for categorical fields.
- Numeric coercion with `pd.to_numeric(errors="coerce")`.
- **Missing value handling** (the real dataset has none, but the
  pipeline handles it defensively for any future data):
  - Numeric fields are median-imputed inside the pipeline.
  - Categorical fields are imputed with the most frequent value.
- **Encoding**: One-Hot Encoding for `gender`, `smoker`, `region`.
- **Scaling**: StandardScaler applied to all numeric features.
- All preprocessing is wrapped in a scikit-learn `ColumnTransformer` +
  `Pipeline`, so the exact same transformation is guaranteed at both
  training and inference time (no train/serve skew).

## 6. Feature Engineering

- **BMI** is derived from height and weight (`weight_kg / height_m²`)
  rather than requiring manual entry — reduces input error and reflects
  a realistic clinical formula.
- BMI category (Underweight / Normal / Overweight / Obese) is displayed
  alongside predictions for interpretability.

## 7. Model Training & Comparison

`train_model.py` trains and evaluates three regression models on an
80/20 train-test split:

1. **Linear Regression** — baseline linear model.
2. **Decision Tree Regressor** — captures non-linear interactions.
3. **Random Forest Regressor** — ensemble of trees, typically the
   strongest performer on this type of tabular data.

For each model it reports:

- **R² Score** (accuracy / variance explained)
- **MAE** (Mean Absolute Error)
- **MSE** (Mean Squared Error)
- **RMSE** (Root Mean Squared Error)

The model with the **highest R² score** is automatically selected,
saved to `model/premium_model.pkl` via Joblib, and its metrics are
written to `model/metrics.json` for reference.

## 8. Results

Actual results on the real dataset (80/20 train-test split, seed 42):

| Model                   | R²     | MAE ($) | RMSE ($) |
|--------------------------|--------|---------|----------|
| Linear Regression        | 0.7836 | 4181.19 | 5796.28  |
| Decision Tree Regressor  | 0.8424 | 2668.75 | 4945.71  |
| Random Forest Regressor  | 0.8762 | 2409.12 | 4383.42  |

**Random Forest Regressor** is selected as the best model. Smoking
status is by far the strongest predictor of charges in this dataset —
smokers are charged several times more on average than non-smokers —
followed by age and BMI.

## 9. Application Features

### Predict Premium
Single-applicant form with input validation, automatic BMI calculation,
one-click prediction, a confidence score (derived from model R², shown
as an SVG gauge), and a downloadable **CSV** of the result.

### UI
Modern card-based layout with a **light/dark mode toggle**, a responsive
sidebar (collapses to a hamburger menu on mobile), smooth hover/transition
effects, and inline SVG icons — all built with plain CSS, no component
library.

## 10. Project Structure

The project is organized into two independent, self-contained halves —
a Python backend and a static frontend — each with its own dependencies
(the frontend has none; it's plain HTML/CSS/JS with no build step).

```text
HealthInsurancePremiumPrediction/
│
├── backend/
│   ├── main.py               # FastAPI application (JSON API)
│   ├── predict.py            # PremiumPredictor class (inference)
│   ├── train_model.py        # Model training & comparison pipeline
│   ├── requirements.txt      # Backend (Python) dependencies
│   ├── .venv/                # Backend virtual environment
│   ├── dataset/
│   │   ├── insurance.csv     # Real "Medical Cost Personal Datasets" data
│   │   └── fetch_dataset.py  # Downloads the dataset from its public mirror
│   ├── model/
│   │   ├── premium_model.pkl # Best trained model (Joblib)
│   │   └── metrics.json      # Model comparison metrics
│   └── utils/
│       └── preprocessing.py  # Shared preprocessing/validation logic
│
├── frontend/                 # Plain HTML / CSS / JS — no build step
│   ├── index.html            # Predict Premium page
│   ├── css/
│   │   └── style.css         # Single shared stylesheet (design tokens, layout, components)
│   └── js/
│       ├── api.js            # Fetch API wrapper for the backend
│       ├── theme.js          # Dark mode + mobile sidebar toggle
│       ├── layout.js         # Fills shared sidebar/nav markup + icons
│       ├── icons.js          # Inline SVG icon set
│       └── predict.js        # Predict Premium page logic (incl. gauge chart)
│
└── README.md
```

## 11. How to Run

```bash
# 1. Set up the backend (from backend/)
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2. (Optional) Re-download the dataset
python dataset/fetch_dataset.py

# 3. Train the model
python train_model.py

# 4. Start the backend API (still from backend/)
uvicorn main:app --reload --port 8000

# 5. In a separate terminal, serve the frontend as static files
cd frontend
python -m http.server 5500
```

Then open `http://localhost:5500` in your browser. Any static file
server works (Python's `http.server`, VS Code's "Live Server" extension,
etc.) — the frontend has no dependencies to install. It talks to the
API at `http://localhost:8000` (change `API_BASE` in `frontend/js/api.js`
if you run the backend on a different host/port).

## 12. Future Enhancements

- Combine this dataset with additional real-world insurance data for a
  larger, more diverse training set.
- Add hyperparameter tuning (GridSearchCV / Optuna) for each model.
- Add SHAP-based explainability to show per-prediction feature impact.
- Support user accounts and prediction history (would require a
  database — intentionally out of scope for this project).
- Deploy the backend (Docker/Render/Fly.io) and frontend
  (Vercel/Netlify) for public access.
- Add additional models (XGBoost, Gradient Boosting) to the comparison.

## 13. Screenshots

_Add screenshots of the running application to the `screenshots/`
folder and reference them here, e.g.:_

```markdown
![Prediction Page](screenshots/predict.png)
![Dashboard](screenshots/dashboard.png)
```
