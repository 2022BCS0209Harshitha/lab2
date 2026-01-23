from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np

app = FastAPI(title="Wine Quality Predictor")

model = joblib.load("model.joblib")

class PredictRequest(BaseModel):
    features: List[float]

@app.get("/")
def root():
    return {"name": "Harshitha", "roll_no": "2022BCS0209", "status": "API running"}

@app.post("/predict")
def predict(req: PredictRequest):
    if len(req.features) != 11:
        return {"error": "Exactly 11 values required"}

    X = np.array(req.features, dtype=float).reshape(1, -1)
    pred = model.predict(X)[0]
    return {"name": "Harshitha", "roll_no": "2022BCS0209", "wine_quality": int(round(pred))}
