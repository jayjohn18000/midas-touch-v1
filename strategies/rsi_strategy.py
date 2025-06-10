import pandas as pd

def rsi_strategy(df, period=14, lower=30, upper=70):
    df = df.copy()
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["Signal"] = 0
    df.loc[df["RSI"] < lower, "Signal"] = 1   # Buy
    df.loc[df["RSI"] > upper, "Signal"] = -1  # Sell

    return df
