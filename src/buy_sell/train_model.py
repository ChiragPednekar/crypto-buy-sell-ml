import pandas as pd
import joblib
import os
import sys
import numpy as np

import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import TimeSeriesSplit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils.class_weight import compute_class_weight

# Local config import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src import model_config as config

def load_data():
    return pd.read_csv("data/processed/crypto_features.csv")

def run_triple_barrier(df, k1, k2, max_period):
    """Calculates target using path-dependent max holding period and trailing bands."""
    targets = np.ones(len(df)) # Default HOLD
    close_vals = df["close"].values
    atr_vals = df["atr"].values
    
    for i in range(len(close_vals) - 1): # Exclude last item
        cp = close_vals[i]
        tp = cp + k1 * atr_vals[i]
        sl = cp - k2 * atr_vals[i]
        
        limit = min(i + 1 + max_period, len(close_vals))
        path = close_vals[i+1 : limit]
        
        for p in path:
            if p >= tp:
                targets[i] = 2 # BUY
                break
            elif p <= sl:
                targets[i] = 0 # SELL
                break
    return targets

def apply_target_engineering(df):
    """Replaces fixed threshold labeling with ATR-volatility adjusted labels or Triple-Barrier."""
    if config.TARGET_METHOD == "triple_barrier":
        print("Using Triple Barrier Path Dependent Labeling...")
        df["target"] = run_triple_barrier(df, config.TB_TAKE_PROFIT_K, config.TB_STOP_LOSS_K, config.TB_MAX_PERIOD)
        # Drop rows with insufficient forward vision
        df = df.iloc[:-config.TB_MAX_PERIOD]
    else:
        print("Using Volatility-Adjusted Target Windows...")
        # future price difference over N steps vs standard absolute unit of ATR
        df["future_diff"] = df["close"].shift(-config.N_STEPS) - df["close"]
        df["upper_threshold"] = config.ATR_K * df["atr"]
        df["lower_threshold"] = -config.ATR_K * df["atr"]
        
        df["target"] = np.where(df["future_diff"] > df["upper_threshold"], 2, 
                         np.where(df["future_diff"] < df["lower_threshold"], 0, 1))
        df = df.dropna(subset=["future_diff"])
        df = df.drop(columns=["future_diff", "upper_threshold", "lower_threshold"])
        
    return df

def feature_selection(model, X, y):
    """Simple Tree-based importance ranking to drop noise features."""
    if not config.DROP_LOW_IMPORTANCE:
         return X.columns.tolist()

    # Fit small uncalibrated base model simply to peek at features
    print("Evaluating Feature Impurities...")
    model.fit(X, y)
    
    # Check if Voting or Native
    top_features_agg = np.zeros(X.shape[1])
    
    if hasattr(model, 'estimators_'):
        for est in model.estimators_:
             if hasattr(est, 'feature_importances_'):
                 top_features_agg += est.feature_importances_
        importance = top_features_agg / len(model.estimators_)
    else:
        importance = model.feature_importances_
        
    feat_imp = pd.Series(importance, index=X.columns).sort_values(ascending=False)
    
    print("\nTop 10 Important Features:")
    print(feat_imp.head(10))
    top_k = feat_imp.head(config.TOP_K_FEATURES).index.tolist()
    return top_k

def build_ensemble():
    """Builds Calibrated Voting Ensemble Model with dynamic class weighting."""
    xgb_opts = {"n_estimators": 150, "learning_rate": 0.05, "max_depth": 5, "eval_metric": 'mlogloss'}
    rf_opts = {"n_estimators": 150, "max_depth": 8, "random_state": 42}
    
    if config.BALANCE_CLASSES:
        rf_opts['class_weight'] = 'balanced'
    
    clf_xgb = xgb.XGBClassifier(**xgb_opts)
    clf_rf = RandomForestClassifier(**rf_opts)
    
    estimators = [('xgb', clf_xgb), ('rf', clf_rf)]
    weights = [config.XGB_WEIGHT, config.RF_WEIGHT]
    
    try:
        import lightgbm as lgb
        lgb_opts = {"n_estimators": 150, "learning_rate": 0.05, "max_depth": 5, "verbose": -1}
        if config.BALANCE_CLASSES:
             lgb_opts['class_weight'] = 'balanced'
        clf_lgb = lgb.LGBMClassifier(**lgb_opts)
        estimators.append(('lgb', clf_lgb))
        weights.append(config.LGBM_WEIGHT)
    except ImportError:
        print("Note: LightGBM not installed. Running ensemble heavily weighted on XGBoost/RF.")
        weights = [0.6, 0.4] # Normalized fallback
        
    # Voting ensemble handles averaging
    ensemble = VotingClassifier(estimators=estimators, voting='soft', weights=weights)
    
    if config.CALIBRATE_PROBS:
        # Wrap in probability corrector (sigmoid better for smaller multi-class arrays than isotonic without big margins)
        model = CalibratedClassifierCV(ensemble, method='sigmoid', cv=3)
    else:
        model = ensemble
        
    return model

def main():
    data = load_data()
    data = apply_target_engineering(data)
    
    # Avoid data leaks (timestamp) and redundant labels
    drop_cols = ["timestamp", "target"]
    drop_cols = [c for c in drop_cols if c in data.columns]
    
    X = data.drop(columns=drop_cols)
    y = data["target"].astype(int)
    
    # Feature selector module
    clf_selector = RandomForestClassifier(n_estimators=50, random_state=42)
    kept_features = feature_selection(clf_selector, X, y)
    X = X[kept_features]
    
    print(f"\nTraining on {len(X)} rows with {len(X.columns)} features.")
    
    tscv = TimeSeriesSplit(n_splits=config.WF_SPLITS)
    model = build_ensemble()
    
    print("\n--- Walk-Forward Validation Results ---")
    
    accuracies = []
    
    # Rolling forward cross-val logic
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
        
        # NOTE: Using class_weight='balanced' directly in RF and LGBM params. 
        # XGB handles natively through binary params, or soft balancing logic handled naturally by ensembling combined.
        # Strict sample_weight fit parameters bypass CalibratedClassifierCV pipelines, so we lean towards native.
        
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        
        print(f"Fold {fold+1} Accuracy: {acc:.4f}")
        accuracies.append(acc)
        
    print(f"\nMean CV Accuracy: {np.mean(accuracies):.4f}")
    
    # Retrain on full dataset
    print("\nRefitting Global Mode for Production Use...")
    model.fit(X, y)
    preds = model.predict(X)
    print("\nFinal Global Classification Report:")
    print(classification_report(y, preds, target_names=['SELL', 'HOLD', 'BUY']))
    
    # Save Pipeline Assets
    os.makedirs("models", exist_ok=True)
    metadata = {
        "features": kept_features,
        "classes": ['SELL', 'HOLD', 'BUY']
    }
    joblib.dump(model, "models/buy_sell_model.pkl")
    joblib.dump(metadata, "models/model_metadata.pkl")
    
    print("\nModel saved to models/buy_sell_model.pkl")
    print("Metadata saved to models/model_metadata.pkl")

if __name__ == "__main__":
    main()
