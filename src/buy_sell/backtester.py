import pandas as pd
import joblib

model = joblib.load("models/buy_sell_model.pkl")

data = pd.read_csv("data/processed/crypto_features.csv")

data["target"] = (data["close"].shift(-1) > data["close"]).astype(int)
data = data.dropna()

X = data.drop(columns=["timestamp","target"])

preds = model.predict(X)

data["prediction"] = preds

# strategy returns

data["strategy_return"] = data["prediction"] * data["returns"]

# cumulative returns

strategy_profit = (1 + data["strategy_return"]).cumprod().iloc[-1]
buy_hold = (1 + data["returns"]).cumprod().iloc[-1]

print("\nStrategy Profit:", round((strategy_profit-1)*100,2), "%")
print("Buy & Hold Profit:", round((buy_hold-1)*100,2), "%")
