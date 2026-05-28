from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

model = joblib.load("models/buy_sell_model.pkl")

@app.get("/predict")
def predict():
    df = pd.read_csv("data/processed/crypto_features.csv")
    latest = df.tail(1)
    probs = model.predict_proba(latest)[0]

    return {
        "hold_prob": float(probs[0]),
        "buy_prob": float(probs[1]),
        "sell_prob": float(probs[2])
    }