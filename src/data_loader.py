from binance.client import Client
import pandas as pd

client = Client()

symbol = "BTCUSDT"
interval = Client.KLINE_INTERVAL_1HOUR

klines = client.get_historical_klines(
    symbol,
    interval,
    "1 Jan, 2020"
)

data = []

for k in klines:
    data.append({
        "timestamp": k[0],
        "open": float(k[1]),
        "high": float(k[2]),
        "low": float(k[3]),
        "close": float(k[4]),
        "volume": float(k[5])
    })

df = pd.DataFrame(data)

df.to_csv("data/raw/crypto_raw_data.csv", index=False)

print("Data saved to data/raw/crypto_raw_data.csv")