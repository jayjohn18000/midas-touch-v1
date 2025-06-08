import os
os.makedirs('results', exist_ok=True)
apt import pandas as pd
from strategies.sma_crossover import sma_crossover_strategy
from backtester.engine import backtest

df = pd.read_csv('data/historical.csv', parse_dates=['Date'])
df = sma_crossover_strategy(df, short=2, long=3)
results = backtest(df)
results.to_csv('results/equity_curve.csv', index=False)
print("✅ Backtest complete. Results saved to results/equity_curve.csv.")
