import pandas as pd
import numpy as np

def classify_regime(row):
    """
    Classifies the market regime for a single row of features.
    Regimes:
        0 = Sideways
        1 = Trending Up
        2 = Trending Down
        3 = High Volatility
    """
    # Fetch needed features; use dummy defaults if missing in dev pipeline
    adx = row.get("adx", 0)
    volatility = row.get("volatility_20", 0)
    ema_slope = row.get("ema_slope_10", 0)
    macd_slope = row.get("macd_hist_slope", 0)
    # Using ATR normalized against price 
    atr_norm = row.get("atr", 0) / row.get("close", 1)
    
    # Simple rule-based logic designed for later ML classification dropping
    # High volatility state (e.g. > 2.5% simple roll vol or outsized ATR vs close)
    if volatility > 0.025 or atr_norm > 0.01:
        return 3
    # Active trend threshold
    elif adx > 25:
        # Check alignment of simple moving trend and momentum
        if ema_slope > 0 and macd_slope >= 0:
            return 1 # Uptrend
        elif ema_slope < 0 and macd_slope <= 0:
            return 2 # Downtrend
        else:
            # Conflicting signals in trend
            return 1 if ema_slope > 0 else 2 
    else:
        # Low ADX -> Sideways
        return 0

def add_regime_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely calculates needed derived slope features for regime and adds the regime output.
    Allows for future ML/HMM replacing `classify_regime`.
    """
    if "ema12" in df.columns and "ema_slope_10" not in df.columns:
        df["ema_slope_10"] = df["ema12"].diff(10).fillna(0)
    elif "close" in df.columns and "ema_slope_10" not in df.columns:
        df["ema_slope_10"] = df["close"].diff(10).fillna(0)
        
    if "macd_hist" in df.columns and "macd_hist_slope" not in df.columns:
        df["macd_hist_slope"] = df["macd_hist"].diff(3).fillna(0)
        
    df["regime"] = df.apply(classify_regime, axis=1)
    return df
