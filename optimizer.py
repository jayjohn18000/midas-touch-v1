import json
import itertools
import os
import pandas as pd
from run_backtest import run_backtest
from strategies.backtrader_strategies import SMACrossoverStrategy, RSIStrategy, PNShootStrategy

# === Mapping strategy names to classes ===
strategy_map = {
    "sma_crossover": SMACrossoverStrategy,
    "rsi": RSIStrategy,
    "pnshoot": PNShootStrategy
}

# === Load parameter grid from config file ===
def load_param_grid(strategy_name):
    with open("config/parameter_config.json") as f:
        param_space = json.load(f)
    return param_space[strategy_name]

# === Cartesian product of parameter combinations ===
def generate_param_combinations(param_grid):
    keys, values = zip(*param_grid.items())
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))

# === Run backtests for all parameter combinations ===
def optimize_strategy(symbol, strategy_name):
    strategy_class = strategy_map[strategy_name]
    param_grid = load_param_grid(strategy_name)

    results = []

    for param_combo in generate_param_combinations(param_grid):
        print(f"🔍 Testing: {param_combo}")
        run_id = f"{symbol}_{strategy_name}_" + "_".join(f"{k}{v}" for k,v in param_combo.items())

        try:
            _, metrics = run_backtest(
                symbol=symbol,
                strategy_class=strategy_class,
                strategy_name=strategy_name,
                save_path=f"results/optimizations/{run_id}.csv",
                **param_combo
            )
            if metrics:
                results.append({**param_combo, **metrics})
        except Exception as e:
            print(f"❌ Failed run {run_id}: {e}")

    # Save all successful run metrics
    if results:
        df = pd.DataFrame(results)
        os.makedirs("results/optimizations", exist_ok=True)
        df.to_csv(f"results/optimizations/summary_{strategy_name}_{symbol}.csv", index=False)
        print("✅ Optimization complete.")
    else:
        print("⚠️ No successful runs.")

# === CLI entry point ===
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g., AAPL)")
    parser.add_argument("--strategy", required=True, choices=strategy_map.keys())
    args = parser.parse_args()

    optimize_strategy(args.symbol, args.strategy)
