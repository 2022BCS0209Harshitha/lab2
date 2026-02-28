from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="Wine Quality Prediction API")

NAME = "Harshitha"
ROLL_NO = "2022BCS0209"

# IMPORTANT: Dockerfile copies model.joblib into /app/model.joblib
model = joblib.load("model.joblib")


class WineFeatures(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def home():
    return {"status": "ok", "service": "wine-quality-inference"}


@app.post("/predict")
def predict(features: WineFeatures):
    x = np.array([[
        features.fixed_acidity,
        features.volatile_acidity,
        features.citric_acid,
        features.residual_sugar,
        features.chlorides,
        features.free_sulfur_dioxide,
        features.total_sulfur_dioxide,
        features.density,
        features.pH,
        features.sulphates,
        features.alcohol
    ]], dtype=float)

    pred = model.predict(x)[0]
    wine_quality = int(round(float(pred)))

    return {
        "name": NAME,
        "roll_no": ROLL_NO,
        "wine_quality": wine_quality
    }
