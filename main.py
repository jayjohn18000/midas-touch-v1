
import argparse
import os
import pandas as pd
from fetch_data import fetch_data
from run_backtest import run_backtest
from strategies.backtrader_strategies import SMACrossoverStrategy, RSIStrategy, PNShootStrategy
from data.soapy_symbols import clean_crypto_pairs, clean_crypto_public, clean_quant_public
import re
import csv
from multiprocessing import Pool, cpu_count

# === Strategy Mapping ===
# Map strategy names (as used in CLI or task list) to actual Backtrader-compatible strategy classes
strategy_map = {
    "sma_crossover": SMACrossoverStrategy,
    "rsi": RSIStrategy,
    "pnshoot": PNShootStrategy
}

# === Ticker Validation ===
# Ensure ticker strings are in a valid format
def is_valid_ticker(ticker):
    return isinstance(ticker, str) and re.match(r'^[A-Z0-9\.\-]{1,10}$', ticker.strip())

# === Load Symbols from CSV ===
# Load and combine cleaned symbol lists from crypto and quant CSVs
def load_symbols_from_csv():
    tickers = set(
        clean_crypto_pairs("data/symbols/crypto_pairs.csv") +
        clean_crypto_public("data/symbols/crypto_public.csv") +
        clean_quant_public("data/symbols/quant_public.csv")
    )
    return sorted(tickers)

# === Core Backtest Execution Function ===
# This gets called per (symbol, strategy) pair in parallel
def run_backtest_combo(args_tuple):
    symbol, strategy_name = args_tuple
    strategy_class = strategy_map[strategy_name]
    try:
        # Fetch historical data
        df = fetch_data(symbol)
        if df is None or df.empty:
            raise ValueError("No valid data")

        # Run the backtest
        results, metrics = run_backtest(
            symbol=symbol,
            strategy_class=strategy_class,
            strategy_name=strategy_name,
            save_path=f"results/equity_curves/{strategy_name}/{symbol}.csv"
        )

        # Check if results are usable
        if results is None or not isinstance(results, list) or len(results) == 0:
            raise ValueError("Backtest returned no usable results")
        if not metrics or not isinstance(metrics, dict):
            raise ValueError("Metrics were not returned properly")

        # Return summary row
        return {
            "Symbol": symbol,
            "Strategy": strategy_name,
            **metrics
        }

    except Exception as e:
        # Log failure
        print(f"❌ Error on {symbol} [{strategy_name}]: {e}")
        return {
            "Symbol": symbol,
            "Strategy": strategy_name,
            "Error": str(e)
        }

# === Main Execution ===
# Runs a full backtest suite over selected strategies and symbols
def main():
    parser = argparse.ArgumentParser(description="Backtest multiple strategies across symbols.")
    parser.add_argument("--symbol", help="Single ticker symbol (e.g. SOL-USD)")
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default="2025-05-01")
    args = parser.parse_args()

    # Load symbols: either just one, or all from CSVs
    symbols = [args.symbol] if args.symbol else load_symbols_from_csv()
    strategy_names = list(strategy_map.keys())

    # Prepare output directories
    os.makedirs("results", exist_ok=True)
    for s in strategy_names:
        os.makedirs(f"results/equity_curves/{s}", exist_ok=True)

    # Clear failure log
    with open("results/failures.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol", "Strategy", "Error"])

    # Create workload list
    tasks = [(symbol, strategy) for strategy in strategy_names for symbol in symbols]
    print(f"🚀 Running {len(tasks)} backtests using {min(cpu_count(), 4)} cores...")

    # Execute in parallel
    with Pool(processes=min(cpu_count(), 4)) as pool:
        results = pool.map(run_backtest_combo, tasks)

    # Separate successes and failures
    all_summaries = []
    all_failures = []

    for r in results:
        if "Error" in r:
            all_failures.append(r)
        else:
            all_summaries.append(r)

    # Save summaries per strategy and all together
    if all_summaries:
        df = pd.DataFrame(all_summaries)
        for strategy in strategy_names:
            df[df["Strategy"] == strategy].to_csv(f"results/summary_{strategy}.csv", index=False)
        df.to_csv("results/summary_all.csv", index=False)
        print("✅ Summaries saved.")

    # Save any failures
    if all_failures:
        with open("results/failures.csv", "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Symbol", "Strategy", "Error"])
            writer.writerows(all_failures)
        print("⚠️ Failures logged.")

# Entry point
if __name__ == "__main__":
    main()
