import numpy as np

def generate_signal(probabilities, regime_label, config):
    buy_prob = probabilities[1]
    sell_prob = probabilities[2]

    buy_threshold = config["thresholds"]["buy_prob"]
    sell_threshold = config["thresholds"]["sell_prob"]

    # Regime filter
    if regime_label == "bear":
        if sell_prob > sell_threshold:
            return "SELL"
        return "HOLD"

    if regime_label == "bull":
        if buy_prob > buy_threshold:
            return "BUY"
        return "HOLD"

    # sideways
    if buy_prob > buy_threshold:
        return "BUY"
    if sell_prob > sell_threshold:
        return "SELL"

    return "HOLD"