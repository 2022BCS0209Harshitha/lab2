from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np

app = FastAPI(title="Wine Quality Predictor")

# load trained model
model = joblib.load("model.joblib")

# ✅ this fixes Swagger schema
class PredictRequest(BaseModel):
    features: List[float]

@app.get("/")
def root():
    return {
        "name": "Harshitha",
        "roll_no": "2022BCS0209",
        "status": "API running"
    }

@app.post("/predict")
def predict(request: PredictRequest):
    if len(request.features) != 11:
        return {
            "name": "Harshitha",
            "roll_no": "2022BCS0209",
            "error": "Exactly 11 features required"
        }

    X = np.array(request.features, dtype=float).reshape(1, -1)
    prediction = model.predict(X)[0]

    return {
        "name": "Harshitha",
        "roll_no": "2022BCS0209",
        "wine_quality": int(round(prediction))
    }
