import numpy as np

class RiskManager:

    def __init__(self, risk_per_trade=0.01):
        self.risk_per_trade = risk_per_trade

    def position_size(self, capital, entry_price, stop_loss_price):
        risk_amount = capital * self.risk_per_trade
        stop_distance = abs(entry_price - stop_loss_price)

        if stop_distance == 0:
            return 0

        quantity = risk_amount / stop_distance
        return round(quantity, 5)

    def calculate_stop_loss(self, entry_price, atr, multiplier=1.5):
        return entry_price - (atr * multiplier)

    def calculate_take_profit(self, entry_price, atr, multiplier=2):
        return entry_price + (atr * multiplier)