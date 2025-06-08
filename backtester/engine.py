import pandas as pd

def backtest(df_with_signals, starting_cash=10000):
    df = df_with_signals.copy()
    cash = starting_cash
    position = 0
    equity_curve = []

    for i in range(1, len(df)):
        price = df.iloc[i]['Close']
        signal = df.iloc[i]['Signal']

        # Buy
        if signal == 1 and position == 0:
            position = cash / price
            cash = 0
        # Sell
        elif signal == -1 and position > 0:
            cash = position * price
            position = 0

        total_value = cash + (position * price if position > 0 else 0)
        equity_curve.append(total_value)

    df = df.iloc[1:].copy()
    df['Equity'] = equity_curve
    return df
