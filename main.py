import argparse
import os
import pandas as pd
from fetch_data import fetch_data
from run_backtest import run_backtest
from strategies.sma_crossover import sma_crossover_strategy
from strategies.rsi_strategy import rsi_strategy
from strategies.pnshoot_strategy import PNShoot
from data.soapy_symbols import clean_crypto_pairs, clean_crypto_public, clean_quant_public
import re
import csv
from multiprocessing import Pool, cpu_count

# Map strategy names to functions
strategy_map = {
    "sma_crossover": sma_crossover_strategy,
    "rsi": rsi_strategy,
    "pnshoot" : PNShoot
}

def is_valid_ticker(ticker):
    return isinstance(ticker, str) and re.match(r'^[A-Z0-9\.\-]{1,10}$', ticker.strip())

def load_symbols_from_csv():
    tickers = set(
        clean_crypto_pairs("data/symbols/crypto_pairs.csv") +
        clean_crypto_public("data/symbols/crypto_public.csv") +
        clean_quant_public("data/symbols/quant_public.csv")
    )
    return sorted(tickers)

def run_backtest_combo(args_tuple):
    symbol, strategy_name = args_tuple
    strategy_fn = strategy_map[strategy_name]
    try:
        df = fetch_data(symbol)
        if df is None or df.empty:
            raise ValueError("No valid data")

        results, metrics = run_backtest(
            symbol=symbol,
            strategy_fn=strategy_fn,
            strategy_name=strategy_name,
            save_path=f"results/equity_curves/{strategy_name}/{symbol}.csv"
        )


        if results is None or results.empty or 'Equity' not in results.columns:
            raise ValueError("Backtest returned no usable results")

        return {
            "Symbol": symbol,
            "Strategy": strategy_name,
            **metrics
        }

    except Exception as e:
        print(f"❌ Error on {symbol} [{strategy_name}]: {e}")
        return {
            "Symbol": symbol,
            "Strategy": strategy_name,
            "Error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Backtest multiple strategies across symbols.")
    parser.add_argument("--symbol", help="Single ticker symbol (e.g. SOL-USD)")
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default="2025-05-01")
    args = parser.parse_args()

    symbols = [args.symbol] if args.symbol else load_symbols_from_csv()
    strategy_names = list(strategy_map.keys())
    os.makedirs("results", exist_ok=True)

    # Clear failures file
    with open("results/failures.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol", "Strategy", "Error"])

    # Create output folders
    for s in strategy_names:
        os.makedirs(f"results/equity_curves/{s}", exist_ok=True)

    # Create all (symbol, strategy) combinations
    tasks = [(symbol, strategy) for strategy in strategy_names for symbol in symbols]

    print(f"🚀 Running {len(tasks)} backtests using {min(cpu_count(), 4)} cores...")

    with Pool(processes=min(cpu_count(), 4)) as pool:
        results = pool.map(run_backtest_combo, tasks)

    # Save results
    all_summaries = []
    all_failures = []

    for r in results:
        if "Error" in r:
            all_failures.append(r)
        else:
            all_summaries.append(r)

    if all_summaries:
        df = pd.DataFrame(all_summaries)
        for strategy in strategy_names:
            df[df["Strategy"] == strategy].to_csv(f"results/summary_{strategy}.csv", index=False)
        df.to_csv("results/summary_all.csv", index=False)
        print("✅ Summaries saved.")

    if all_failures:
        with open("results/failures.csv", "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Symbol", "Strategy", "Error"])
            writer.writerows(all_failures)
        print("⚠️ Failures logged.")

if __name__ == "__main__":
    main()
