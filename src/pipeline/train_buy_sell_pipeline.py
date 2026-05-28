import pandas as pd
import yaml
from src.buy_sell.buy_sell_model import BuySellModel

def create_labels(df, future_window=3):
    df["future_return"] = df["close"].shift(-future_window) / df["close"] - 1

    conditions = [
        df["future_return"] > 0.01,
        df["future_return"] < -0.01
    ]

    choices = [1, 2]
    df["label"] = 0
    df.loc[conditions[0], "label"] = 1
    df.loc[conditions[1], "label"] = 2

    return df.dropna()

def train_pipeline():
    with open("src/config/config.yaml") as f:
        config = yaml.safe_load(f)

    df = pd.read_csv("data/processed/crypto_features.csv")

    df = create_labels(df)

    X = df.drop(["label"], axis=1)
    y = df["label"]

    model = BuySellModel(config)
    model.train(X, y)
    model.save("models/buy_sell_model.pkl")

if __name__ == "__main__":
    train_pipeline()