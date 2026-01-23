from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from typing import List, Optional, Dict, Any

app = FastAPI()

model = joblib.load("model.joblib")

class PredictRequest(BaseModel):
    features: Optional[List[float]] = None
    # allow alternate payloads too
    data: Optional[List[float]] = None

@app.post("/predict")
def predict(req: PredictRequest):
    vec = req.features or req.data
    if vec is None:
        return {
            "name": "Harshitha",
            "roll_no": "2022BCS0209",
            "error": "Please send JSON with key 'features' (or 'data') as a list of 11 numbers."
        }

    X = np.array(vec, dtype=float).reshape(1, -1)
    pred = model.predict(X)[0]

    return {
        "name": "Harshitha",
        "roll_no": "2022BCS0209",
        "wine_quality": int(round(pred))
    }
