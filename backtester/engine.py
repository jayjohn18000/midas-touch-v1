import pandas as pd
import numpy as np

def backtest(df_with_signals, starting_cash=10000):
    df = df_with_signals.copy()
    cash = starting_cash
    position = 0
    equity_curve = []
    trades = []
    wins = 0
    last_buy_price = None

    for i in range(1, len(df)):
        price = df.iloc[i]['Close']
        signal = df.iloc[i]['Signal']

        # Buy
        if signal == 1 and position == 0:
            position = cash / price
            last_buy_price = price
            cash = 0
            trades.append(('BUY', price))

        # Sell
        elif signal == -1 and position > 0:
            cash = position * price
            if price > last_buy_price:
                wins += 1
            position = 0
            trades.append(('SELL', price))

        total_value = cash + (position * price if position > 0 else 0)
        equity_curve.append(total_value)

    df = df.iloc[1:].copy()
    df['Equity'] = equity_curve

    # Compute metrics
    start_value = equity_curve[0]
    end_value = equity_curve[-1]
    pct_return = round((end_value - start_value) / start_value * 100, 2)
    returns = pd.Series(equity_curve).pct_change().dropna()
    sharpe = round((returns.mean() / returns.std()) * np.sqrt(252), 2) if not returns.empty else 0

    rolling_max = pd.Series(equity_curve).cummax()
    drawdown = (pd.Series(equity_curve) - rolling_max) / rolling_max
    max_drawdown = round(drawdown.min() * 100, 2)

    metrics = {
        "Start Equity": round(start_value, 2),
        "End Equity": round(end_value, 2),
        "Percent Return": pct_return,
        "Total Trades": len(trades) // 2,
        "Win Rate": round((wins / max(1, len(trades) // 2)) * 100, 2),
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_drawdown
    }
    metrics = {k: float(v) if hasattr(v, 'item') else v for k, v in metrics.items()}

    return df, metrics
