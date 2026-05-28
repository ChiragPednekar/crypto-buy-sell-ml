from src.pipeline.inference_pipeline import run_inference
import websocket
import json
import pandas as pd
import ssl
import pickle
from collections import deque

# Load regime model
model = pickle.load(open("model.pkl", "rb"))

# rolling price buffer
prices = deque(maxlen=50)

def compute_features(price_list):
    df = pd.DataFrame(price_list, columns=["price"])

    df["Return"] = df["price"].pct_change()
    df["Volatility"] = df["Return"].rolling(10).std()
    df["Momentum"] = df["price"].pct_change(5)

    df = df.dropna()

    if len(df) == 0:
        return None

    return df.iloc[-1][["Return","Volatility","Momentum"]].values.reshape(1,-1)


def on_message(ws, message):
    global prices

    data = json.loads(message)

    if "k" not in data:
        return

    price = float(data["k"]["c"])
    prices.append(price)

    features = compute_features(list(prices))
    if features is None:
        return

    # predict regime
    regime = model.predict(features)[0]

    regime_map = {
        0: "bull",
        1: "bear",
        2: "volatile"
    }

    regime_label = regime_map.get(regime, "sideways")

    # convert to dataframe for inference
    latest_row = pd.DataFrame(
        features,
        columns=["Return","Volatility","Momentum"]
    )

    signal = run_inference(latest_row, regime_label)

    print(
        f"Live Price: {price:.2f} | "
        f"Regime: {regime_label.upper()} | "
        f"Signal: {signal}"
    )


def on_error(ws, error):
    print("WebSocket ERROR:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")


def on_open(ws):
    print("Connected to Binance WebSocket stream...")


socket_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

ws = websocket.WebSocketApp(
    socket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever(
    ping_interval=20,
    ping_timeout=10,
    sslopt={"cert_reqs": ssl.CERT_NONE}
)