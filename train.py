import json
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def load_dataset(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")
    df = pd.read_csv(csv_path, sep=";")  # Wine Quality CSV uses ';'
    return df


def build_model(model_type: str, alpha: float):
    model_type = model_type.lower().strip()
    if model_type == "linear":
        return LinearRegression()
    if model_type == "ridge":
        return Ridge(alpha=alpha, random_state=42)
    if model_type == "lasso":
        return Lasso(alpha=alpha, random_state=42, max_iter=10000)
    raise ValueError("model_type must be one of: linear, ridge, lasso")


def main():
    # ========= Experiment knobs (EDIT THESE MANUALLY FOR EACH EXPERIMENT) =========
    MODEL_TYPE = "linear"
    TEST_SIZE = 0.2
    USE_SCALER = False
    K_BEST = 6
           # feature selection: top K numeric features
    RANDOM_STATE = 42
    DATA_PATH = "dataset/winequality-red.csv"
    TARGET_COL = "quality"
    # ===========================================================================

    os.makedirs("outputs", exist_ok=True)

    df = load_dataset(DATA_PATH)

    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found in dataset columns: {list(df.columns)}")

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL].astype(float)

    # All columns are numeric in this dataset, but we keep it general.
    numeric_features = X.columns.tolist()

    numeric_transform_steps = [
        ("imputer", SimpleImputer(strategy="median")),
    ]
    if USE_SCALER:
        numeric_transform_steps.append(("scaler", StandardScaler()))

    numeric_transformer = Pipeline(steps=numeric_transform_steps)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features)
        ],
        remainder="drop"
    )

    selector = SelectKBest(score_func=f_regression, k=min(K_BEST, len(numeric_features)))

    model = build_model(MODEL_TYPE, ALPHA)

    pipeline = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("selectk", selector),
        ("model", model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Print metrics (required)
    print(f"MSE: {mse:.6f}")
    print(f"R2: {r2:.6f}")

    # Save model
    model_path = "outputs/model.joblib"
    joblib.dump(pipeline, model_path)

    # Save results JSON (required)
    results = {
        "mse": float(mse),
        "r2": float(r2),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "experiment": {
            "model_type": MODEL_TYPE,
            "alpha": ALPHA,
            "test_size": TEST_SIZE,
            "use_scaler": USE_SCALER,
            "k_best": K_BEST,
            "random_state": RANDOM_STATE
        }
    }
    results_path = "outputs/results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Helpful line for workflow parsing/logging
    print(f"Saved model to: {model_path}")
    print(f"Saved results to: {results_path}")


if __name__ == "__main__":
    main()
