import pandas as pd
import re

def is_valid_ticker(ticker: str) -> bool:
    return isinstance(ticker, str) and re.match(r'^[A-Z0-9.\-]{1,10}$', ticker.strip())

def clean_crypto_public(filepath: str) -> list:
    df = pd.read_csv(filepath, on_bad_lines='skip', engine='python')

    if "Ticker" not in df.columns:
        raise ValueError("Missing 'Ticker' column in crypto_public.csv")

    # Remove content references and special chars
    df["Ticker"] = df["Ticker"].astype(str).str.extract(r'([A-Z.]+)')[0]
    df = df[df["Ticker"].notnull()]
    df["Ticker"] = df["Ticker"].str.upper().str.strip()

    return sorted([ticker for ticker in df["Ticker"] if is_valid_ticker(ticker)])

def clean_crypto_pairs(filepath: str) -> list:
    df = pd.read_csv(filepath)
    if "Trading Pair" not in df.columns:
        raise ValueError("Missing 'Trading Pair' column in crypto_pairs.csv")

    tickers = df["Trading Pair"].astype(str).str.replace("/", "-", regex=False).str.upper().str.strip()
    return sorted([t for t in tickers if is_valid_ticker(t)])

def clean_quant_public(filepath: str) -> list:
    df = pd.read_csv(filepath, on_bad_lines='skip', engine='python')
    if "Ticker" not in df.columns:
        raise ValueError("Missing 'Ticker' column in quant_public.csv")

    tickers = df["Ticker"].astype(str).str.upper().str.strip()
    return sorted([t for t in tickers if is_valid_ticker(t)])
