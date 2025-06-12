import os
import pandas as pd

def load_csv(path):
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=["Date"]) if "Date" in open(path).readline() else pd.read_csv(path)

def safe_symbol(symbol):
    return symbol.replace("-", "_").replace("/", "_")
