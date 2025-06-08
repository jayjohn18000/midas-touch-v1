import pandas as pd

def sma_crossover_strategy(df, short=5, long=20):
    df = df.copy()
    df['SMA_Short'] = df['Close'].rolling(window=short).mean()
    df['SMA_Long'] = df['Close'].rolling(window=long).mean()
    df['Signal'] = 0
    df.loc[df['SMA_Short'] > df['SMA_Long'], 'Signal'] = 1
    df.loc[df['SMA_Short'] < df['SMA_Long'], 'Signal'] = -1
    return df
