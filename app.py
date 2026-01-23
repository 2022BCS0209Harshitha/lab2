from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load("model.joblib")

@app.get("/")
def root():
    return {
        "name": "Harshitha",
        "roll_no": "2022BCS0209",
        "status": "Wine Quality Prediction API"
    }

@app.post("/predict")
def predict(features: dict):
    """
    Example input:
    {
      "features": [7.4, 0.7, 0.0, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4]
    }
    """
    X = np.array(features["features"]).reshape(1, -1)
    prediction = model.predict(X)[0]
    return {
        "wine_quality": int(round(prediction))
    }
