import os
import sys

# sys.executable ensures that the identical python environment (like .venv) 
# running main.py is consistently passed down to the sub-processes.
PYTHON_BIN = sys.executable

print("Step 1: Downloading crypto data...")
os.system(f'"{PYTHON_BIN}" src/data_loader.py')

print("Step 2: Generating features...")
os.system(f'"{PYTHON_BIN}" src/feature_engineering.py')

print("Step 3: Training buy/sell model...")
os.system(f'"{PYTHON_BIN}" src/buy_sell/train_model.py')

print("Step 4: Training future value model...")
os.system(f'"{PYTHON_BIN}" src/future_value/train_regressor.py')

print("Step 5: Predicting buy/sell signal...")
os.system(f'"{PYTHON_BIN}" src/buy_sell/predict_signal.py')

print("Pipeline complete.")
