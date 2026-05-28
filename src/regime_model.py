import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

def train_regime_model(df, n_states=3):
    # HMM works best with log-returns + volatility features
    features = np.column_stack([
        df["Return"].values,
        df["Volatility"].values
    ])

    # Initialize Gaussian HMM
    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=200,
        random_state=42
    )

    # Fit model
    model.fit(features)

    # Predict hidden states (regimes)
    regimes = model.predict(features)

    df["Regime"] = regimes
    
    return df, model