import sys
import os

# Add the project root (two levels up) to sys.path so 'src' can be imported when running this script directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import yaml
import pandas as pd
import joblib
from src.buy_sell.signal_rules import generate_signal

def run_inference(latest_row, regime_label):
    with open("src/config/config.yaml") as f:
        config = yaml.safe_load(f)

    model = joblib.load("models/buy_sell_model.pkl")

    probs = model.predict_proba(latest_row)[0]

    signal = generate_signal(probs, regime_label, config)

    return signal