import os
import pandas as pd
from strategies.sma_crossover import sma_crossover_strategy
from backtester.engine import backtest

def run_backtest(symbol: str, strategy_fn, strategy_name: str, short=2, long=3, save_path=None):
    safe_symbol = symbol.replace("-", "_").replace("/", "_")
    data_path = f"data/historical_{safe_symbol}.csv"
    
    # If no save_path is provided, use default
    if save_path is None:
        save_path = f"results/equity_curve_{safe_symbol}_{strategy_name}.csv"

    print(f"📊 Running backtest for {symbol} using {strategy_name} strategy...")

    # Load historical data
    df = pd.read_csv(data_path, parse_dates=["Date"])
    df = strategy_fn(df.copy(), short=short, long=long)
    results, metrics = backtest(df)
    print(metrics)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    results.to_csv(save_path, index=False)

    print(f"✅ Backtest complete. Results saved to {save_path}")
    return results, metrics  # return the DataFrame for summary tracking

if __name__ == "__main__":
    run_backtest("SOL-ETH", sma_crossover_strategy, "sma_crossover")



