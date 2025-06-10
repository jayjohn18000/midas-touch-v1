import os
import pandas as pd
from backtester.engine import backtest

def run_backtest(symbol: str, strategy_fn, strategy_name: str, save_path=None, **kwargs):
    safe_symbol = symbol.replace("-", "_").replace("/", "_")
    data_path = f"data/historical_{safe_symbol}.csv"

    if save_path is None:
        save_path = f"results/equity_curve_{safe_symbol}_{strategy_name}.csv"

    print(f"📊 Running backtest for {symbol} using {strategy_name} strategy...")

    try:
        # Load historical data
        df = pd.read_csv(data_path, parse_dates=["Date"])
        
        # Call the strategy function with appropriate kwargs
        df = strategy_fn(df.copy(), **kwargs)

        # Run backtest
        results, metrics = backtest(df)
        print(metrics)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        results.to_csv(save_path, index=False)

        print(f"✅ Backtest complete. Results saved to {save_path}")
        return results, metrics

    except Exception as e:
        print(f"❌ Error during backtest of {symbol}: {e}")
        return None, {}

# Example test
if __name__ == "__main__":
    from strategies.sma_crossover import sma_crossover_strategy
    run_backtest("SOL-ETH", sma_crossover_strategy, "sma_crossover", short=2, long=3)
