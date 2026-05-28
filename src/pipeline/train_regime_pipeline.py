import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import yfinance as yf
import warnings

import pickle

def add_features(df):
    df['Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Return'].rolling(10).std()
    df['Momentum'] = df['Close'].pct_change(5)
    df = df.dropna()
    return df

# download BTC data
df = yf.download("BTC-USD", period="2y")
df = df.reset_index()
df = add_features(df)

X = df[['Return', 'Volatility', 'Momentum']].values

# train model
model = KMeans(n_clusters=3, random_state=42)
model.fit(X)

# save model
pickle.dump(model, open("model.pkl", "wb"))

print("Model trained and saved as model.pkl")