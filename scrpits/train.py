import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

# NOTE: Update this CSV path to match your repo
DATA_PATH = "winequality-red.csv"

def main():
    df = pd.read_csv(DATA_PATH)

    # target column commonly named "quality"
    X = df.drop(columns=["quality"])
    y = df["quality"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    # Save model
    joblib.dump(model, "model.pkl")

    # Save metrics
    with open("metrics.json", "w") as f:
        json.dump({"mse": float(mse), "r2": float(r2)}, f)

    print("Training complete")
    print("MSE:", mse)
    print("R2:", r2)

if __name__ == "__main__":
    main()
