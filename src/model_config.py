# Configuration settings for the quantitative trading model

# -----------------------------------
# FEATURE ENGINEERING & MARKET REGIME
# -----------------------------------
TIMEFRAMES = ["5m", "1h"]

# -----------------------------------
# TARGET & LABELING
# -----------------------------------
TARGET_METHOD = "volatility_adjusted"  # Opts: 'volatility_adjusted', 'triple_barrier'
N_STEPS = 10
ATR_K = 1.0  # k multiplier for upper/lower thresholds in volatility adjusted labeling

# Triple Barrier Parameters
TB_TAKE_PROFIT_K = 2.0  # k1 * ATR for take profit
TB_STOP_LOSS_K = 1.0    # k2 * ATR for stop loss
TB_MAX_PERIOD = 10      # Max holding period

# -----------------------------------
# MODEL CONFIGURATION
# -----------------------------------
USE_ENSEMBLE = True
XGB_WEIGHT = 0.4
LGBM_WEIGHT = 0.3
RF_WEIGHT = 0.3
CALIBRATE_PROBS = True
BALANCE_CLASSES = True

# Feature Selection
DROP_LOW_IMPORTANCE = False
TOP_K_FEATURES = 30

# -----------------------------------
# VALIDATION
# -----------------------------------
WF_SPLITS = 5  # Number of walk-forward validation splits

# -----------------------------------
# PREDICTION & LOGIC
# -----------------------------------
VOL_MAX_THRESHOLD = 0.02

# Expected value sizing parameters
AVG_WIN = 0.015   # Estimated average percentage win  (1.5%)
AVG_LOSS = 0.01   # Estimated average percentage loss (1.0%)
