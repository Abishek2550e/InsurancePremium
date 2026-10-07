"""
backend/main.py
----------------
FastAPI backend for the Health Insurance Premium Prediction System.
Serves the trained model to the plain HTML/CSS/JS frontend.

Run (from the backend/ directory): uvicorn main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from predict import PremiumPredictor, PremiumPredictionError
from utils.preprocessing import compute_bmi

app = FastAPI(title="Health Insurance Premium Prediction API")

app.add_middleware(
    CORSMiddleware,
    # The frontend is plain static HTML/CSS/JS with no fixed dev-server
    # port, so any origin is allowed. No cookies/credentials are used,
    # which keeps a wildcard origin safe for this local student project.
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    predictor = PremiumPredictor()
    predictor_error = None
except PremiumPredictionError as exc:
    predictor = None
    predictor_error = str(exc)


def get_predictor() -> PremiumPredictor:
    if predictor is None:
        raise HTTPException(status_code=503, detail=predictor_error)
    return predictor


class PredictRequest(BaseModel):
    age: int
    gender: str
    height: float
    weight: float
    smoker: str
    children: int
    region: str


class PredictResponse(BaseModel):
    predicted_premium: float
    confidence: float
    model_used: str
    bmi: float


@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": predictor is not None, "error": predictor_error}


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    p = get_predictor()
    record = req.model_dump()
    record["bmi"] = compute_bmi(record["height"], record["weight"])
    try:
        result = p.predict_one(record)
    except PremiumPredictionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {**result, "bmi": record["bmi"]}
