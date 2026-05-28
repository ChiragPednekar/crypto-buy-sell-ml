import pandas as pd
import ta
import numpy as np
import os
import sys

# Add root project dir to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.regime import add_regime_feature

print("Loading raw data...")
df = pd.read_csv("data/raw/crypto_raw_data.csv")

# Ensure timestamp is datetime and sort
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

# =========================
# PRICE FEATURES
# =========================
df["returns"] = df["close"].pct_change()
df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

# =========================
# TREND INDICATORS
# =========================
df["sma20"] = ta.trend.sma_indicator(df["close"], window=20)
df["sma50"] = ta.trend.sma_indicator(df["close"], window=50)

df["ema12"] = ta.trend.ema_indicator(df["close"], window=12)
df["ema26"] = ta.trend.ema_indicator(df["close"], window=26)
df["ema_slope_10"] = df["ema12"].diff(10)

df["macd"] = ta.trend.macd(df["close"])
df["macd_signal"] = ta.trend.macd_signal(df["close"])
df["macd_hist"] = ta.trend.macd_diff(df["close"])
df["macd_hist_slope"] = df["macd_hist"].diff(3) # Derived MACD slope

df["adx"] = ta.trend.adx(df["high"], df["low"], df["close"])

# Market Regime proxy (Historical)
df["regime_trending"] = (df["adx"] > 25).astype(int)

# =========================
# MOMENTUM & LAGS
# =========================
df["rsi"] = ta.momentum.rsi(df["close"], window=14)
df["rsi_lag1"] = df["rsi"].shift(1)
df["rsi_lag2"] = df["rsi"].shift(2)
df["rsi_slope"] = df["rsi"].diff(5) # Derived RSI slope

df["stoch_k"] = ta.momentum.stoch(df["high"], df["low"], df["close"])
df["stoch_d"] = ta.momentum.stoch_signal(df["high"], df["low"], df["close"])

df["cci"] = ta.trend.cci(df["high"], df["low"], df["close"])
df["williams_r"] = ta.momentum.williams_r(df["high"], df["low"], df["close"])

# =========================
# VOLATILITY
# =========================
df["atr"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"])

bb = ta.volatility.BollingerBands(df["close"])
df["bb_high"] = bb.bollinger_hband()
df["bb_low"] = bb.bollinger_lband()
df["bb_width"] = bb.bollinger_wband() # Contains squeeze information inherently

# Z-score of price (Mean reversion metric)
rolling_mean = df["close"].rolling(20).mean()
rolling_std = df["close"].rolling(20).std()
df["price_zscore"] = (df["close"] - rolling_mean) / rolling_std

# =========================
# VOLUME INDICATORS
# =========================
df["obv"] = ta.volume.on_balance_volume(df["close"], df["volume"])
df["mfi"] = ta.volume.money_flow_index(df["high"], df["low"], df["close"], df["volume"])
try:
    df["vwap"] = ta.volume.volume_weighted_average_price(
        df["high"], df["low"], df["close"], df["volume"]
    )
    df["dist_from_vwap"] = (df["close"] - df["vwap"]) / df["vwap"]
except Exception:
    pass # Handle any older library version where VWAP fails gracefully

# =========================
# STAT FEATURES
# =========================
df["volatility_20"] = df["returns"].rolling(20).std()
df["momentum"] = df["close"] - df["close"].shift(10)

# =========================
# MULTI-TIMEFRAME FEATURES (Proxy approach without external files)
# =========================
# We assume base timeframe is 5m. For 1H, multiplier is 12 bounds.
HTF_MUL = 12 
df["htf_ema"] = ta.trend.ema_indicator(df["close"], window=12 * HTF_MUL)
df["htf_rsi"] = ta.momentum.rsi(df["close"], window=14 * HTF_MUL)
df["htf_trend_dir"] = np.where(df["close"] > df["htf_ema"], 1, -1)

# =========================
# MARKET REGIME
# =========================
print("Classifying market regimes...")
df = add_regime_feature(df)

# =========================
# CLEAN DATA
# =========================
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna().reset_index(drop=True)

# Save processed data
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/crypto_features.csv", index=False)

print("Feature engineering complete: Added multi-timeframe, derived slopes, z-scores, and regimes.")
print("Saved to data/processed/crypto_features.csv")