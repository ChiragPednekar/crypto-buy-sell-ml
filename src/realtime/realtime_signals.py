import pandas as pd
from src.pipeline.inference_pipeline import run_inference

def process_realtime_data(df, regime_label):
    latest = df.tail(1)

    signal = run_inference(latest, regime_label)

    print(f"Live Signal: {signal}")
    return signal