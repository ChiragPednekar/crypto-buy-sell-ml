import pandas as pd
import joblib
import os
import sys
import numpy as np

import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

# Local config import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src import model_config as config

def load_data():
    return pd.read_csv("data/processed/crypto_features.csv")

def main():
    data = load_data()
    
    # Target is the price change after N steps: future_close - current_close
    data["target"] = data["close"].shift(-config.N_STEPS) - data["close"]
    
    # Drop rows without future vision
    data = data.dropna(subset=["target"])
    
    # Avoid data leaks (timestamp) and redundant labels
    drop_cols = ["timestamp", "target"]
    drop_cols = [c for c in drop_cols if c in data.columns]
    
    # Load selected features from classifier metadata if available for consistency
    meta_path = "models/model_metadata.pkl"
    if os.path.exists(meta_path):
        try:
            classifier_meta = joblib.load(meta_path)
            kept_features = classifier_meta.get("features", None)
            print("Loaded feature subset from classification metadata.")
        except Exception:
            kept_features = None
    else:
        kept_features = None
        
    X = data.drop(columns=drop_cols)
    if kept_features:
        # Keep only features present in both
        kept_features = [f for f in kept_features if f in X.columns]
        X = X[kept_features]
        
    y = data["target"]
    
    print(f"\nTraining regressor on {len(X)} rows with {len(X.columns)} features.")
    
    # Walk-forward cross validation
    tscv = TimeSeriesSplit(n_splits=config.WF_SPLITS)
    
    xgb_opts = {"n_estimators": 150, "learning_rate": 0.05, "max_depth": 5}
    rf_opts = {"n_estimators": 150, "max_depth": 8, "random_state": 42}
    
    clf_xgb = xgb.XGBRegressor(**xgb_opts)
    clf_rf = RandomForestRegressor(**rf_opts)
    
    estimators = [('xgb', clf_xgb), ('rf', clf_rf)]
    weights = [0.6, 0.4]
    
    try:
        import lightgbm as lgb
        lgb_opts = {"n_estimators": 150, "learning_rate": 0.05, "max_depth": 5, "verbose": -1}
        clf_lgb = lgb.LGBMRegressor(**lgb_opts)
        estimators.append(('lgb', clf_lgb))
        weights = [0.4, 0.3, 0.3]
    except ImportError:
        print("Note: LightGBM not installed. Running ensemble weighted on XGBoost/RF.")
        
    model = VotingRegressor(estimators=estimators, weights=weights)
    
    print("\n--- Walk-Forward Validation Results ---")
    maes = []
    r2s = []
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
        
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        mae = mean_absolute_error(y_val, preds)
        r2 = r2_score(y_val, preds)
        
        print(f"Fold {fold+1} MAE: {mae:.4f} USD | R2: {r2:.4f}")
        maes.append(mae)
        r2s.append(r2)
        
    print(f"\nMean CV MAE: {np.mean(maes):.4f} USD")
    print(f"Mean CV R2: {np.mean(r2s):.4f}")
    
    # Retrain on full dataset
    print("\nRefitting Global Regressor Mode for Production Use...")
    model.fit(X, y)
    
    # Save Regressor Assets
    os.makedirs("models", exist_ok=True)
    metadata = {
        "features": X.columns.tolist(),
        "target_horizon_steps": config.N_STEPS
    }
    joblib.dump(model, "models/future_value_model.pkl")
    joblib.dump(metadata, "models/future_value_metadata.pkl")
    
    print("\nRegressor model saved to models/future_value_model.pkl")
    print("Regressor metadata saved to models/future_value_metadata.pkl")

if __name__ == "__main__":
    main()
