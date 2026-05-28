from binance.client import Client
import os

class BinanceExecutor:

    def __init__(self):
        self.client = Client(
            os.getenv("BINANCE_API_KEY"),
            os.getenv("BINANCE_SECRET_KEY")
        )

    def place_market_order(self, symbol, side, quantity):
        order = self.client.create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )
        return order