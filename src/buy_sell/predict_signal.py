import pandas as pd
import joblib
import json
import numpy as np
import os
import sys

# Local config setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src import model_config as config

STATE_FILE = "trade_state.json"
HISTORY_FILE = "trade_history.csv"

# Pre-load models at module scope so it's not loaded on every API request
try:
    model_path = os.path.join(os.path.dirname(__file__), "../../models/buy_sell_model.pkl")
    meta_path = os.path.join(os.path.dirname(__file__), "../../models/model_metadata.pkl")
    model = joblib.load(model_path)
    metadata = joblib.load(meta_path)
    kept_features = metadata.get("features", None)
except FileNotFoundError:
    model = None
    kept_features = None

try:
    regressor_path = os.path.join(os.path.dirname(__file__), "../../models/future_value_model.pkl")
    regressor_meta_path = os.path.join(os.path.dirname(__file__), "../../models/future_value_metadata.pkl")
    regressor = joblib.load(regressor_path)
    regressor_metadata = joblib.load(regressor_meta_path)
    regressor_features = regressor_metadata.get("features", None)
except FileNotFoundError:
    regressor = None
    regressor_features = None

def get_prediction(execute_trade=False):
    """
    Returns the prediction dict.
    If execute_trade is True, also evaluates logic and tracks state.
    """
    if model is None:
        return {"error": "Model or metadata not found."}

    data_path = os.path.join(os.path.dirname(__file__), "../../data/processed/crypto_features.csv")
    if not os.path.exists(data_path):
         return {"error": "No features found"}
    data = pd.read_csv(data_path)

    latest = data.tail(1).copy()
    current_price = float(latest["close"].values[0])
    current_vol = latest["volatility_20"].values[0]
    
    # get regime if exists
    regime = latest.get("regime", pd.Series([0])).values[0]

    X = latest[kept_features] if kept_features else latest.drop(columns=["timestamp", "target"], errors="ignore")

    probs = model.predict_proba(X)[0] 
    sell_prob = probs[0]
    hold_prob = probs[1]
    buy_prob = probs[2]

    ev_buy = (buy_prob * config.AVG_WIN) - (sell_prob * config.AVG_LOSS)
    ev_sell = (sell_prob * config.AVG_WIN) - (buy_prob * config.AVG_LOSS)

    signal = "HOLD"
    if ev_buy > 0 and ev_buy > ev_sell:
        signal = "BUY"
    elif ev_sell > 0 and ev_sell > ev_buy:
        signal = "SELL"

    predicted_future_price = current_price
    if regressor is not None:
        X_reg = latest[regressor_features] if regressor_features else latest.drop(columns=["timestamp", "target"], errors="ignore")
        predicted_diff = float(regressor.predict(X_reg)[0])
        predicted_future_price = current_price + predicted_diff

    result = {
        "signal": signal,
        "confidence": float(max(buy_prob, sell_prob, hold_prob)),
        "current_price": current_price,
        "regime": int(regime),
        "predicted_future_price": predicted_future_price,
        "volatility": float(current_vol) if not pd.isna(current_vol) else 0.0
    }

    if not execute_trade:
        return result

    # -----------------
    # LOCAL STATE TRADING LOGIC
    # -----------------
    state_path = os.path.join(os.path.dirname(__file__), "../../", STATE_FILE)
    hist_path = os.path.join(os.path.dirname(__file__), "../../", HISTORY_FILE)

    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            state = json.load(f)
    else:
        state = {"position": "NONE", "entry_price": None, "quantity": 1}

    if signal == "BUY" and state["position"] == "NONE":
        state["position"] = "LONG"
        state["entry_price"] = current_price
    elif signal == "SELL" and state["position"] == "LONG":
        exit_price = current_price
        final_pnl = (exit_price - state["entry_price"]) * state["quantity"]
        final_pnl_pct = ((exit_price - state["entry_price"]) / state["entry_price"]) * 100
        
        log_entry = f'{state["entry_price"]},{exit_price},{final_pnl},{final_pnl_pct}\n'
        if not os.path.exists(hist_path):
            with open(hist_path, "w") as f:
                f.write("entry_price,exit_price,pnl,pnl_percentage\n")
        with open(hist_path, "a") as f:
            f.write(log_entry)
            
        state["position"] = "NONE"
        state["entry_price"] = None

    with open(state_path, "w") as f:
        json.dump(state, f)

    pnl = 0.0
    pnl_pct = 0.0
    if state["position"] == "LONG" and state["entry_price"] is not None:
        pnl = (current_price - state["entry_price"]) * state["quantity"]
        pnl_pct = ((current_price - state["entry_price"]) / state["entry_price"]) * 100

    result.update({
        "tracked_state": state,
        "pnl": pnl,
        "pnl_pct": pnl_pct
    })
    
    return result

if __name__ == "__main__":
    res = get_prediction(execute_trade=True)
    if "error" in res:
        print("Error:", res["error"])
        sys.exit(1)
        
    sig = res["signal"]
    cp = res["current_price"]
    
    print("-" * 35)
    print(f"SIGNAL: {sig}")
    print(f"CURRENT PRICE: {cp:.2f}")
    print("-" * 35)