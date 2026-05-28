import numpy as np

def calculate_sharpe(returns, risk_free_rate=0.01):
    excess_returns = returns - risk_free_rate / 252
    sharpe = np.mean(excess_returns) / np.std(excess_returns)
    return sharpe * np.sqrt(252)

def max_drawdown(cumulative_returns):
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    return drawdown.min()