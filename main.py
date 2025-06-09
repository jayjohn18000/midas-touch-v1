import argparse
import os
import pandas as pd
from fetch_data import fetch_data
from run_backtest import run_backtest
from strategies.sma_crossover import sma_crossover_strategy
import re
from data.soapy_symbols import clean_crypto_pairs, clean_crypto_public, clean_quant_public
import csv
from multiprocessing import Pool, cpu_count

# Map strategy names to functions (for future extensibility)
strategy_map = {
    "sma_crossover": sma_crossover_strategy,
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

def run_single_backtest(symbol):
    try:
        strategy_fn = strategy_map["sma_crossover"]
        df = fetch_data(symbol)
        if df is None or df.empty:
            raise ValueError("No valid data")

        results, metrics = run_backtest(
            symbol=symbol,
            strategy_fn=strategy_fn,
            strategy_name="sma_crossover",
            short=2,
            long=3,
            save_path=f"results/equity_curves/{symbol}.csv"
        )

        if results is None or results.empty or 'Equity' not in results.columns:
            raise ValueError("Backtest returned no usable results")

        return {
            "Symbol": symbol,
            "Strategy": "sma_crossover",
            **metrics
        }

    except Exception as e:
        print(f"❌ Error on {symbol}: {e}")
        return {
            "Symbol": symbol,
            "Error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Backtest one symbol or run batch.")
    parser.add_argument("--symbol", help="Single ticker symbol (e.g. SOL-USD)")
    parser.add_argument("--strategy", default="sma_crossover", choices=strategy_map.keys())
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default="2025-05-01")
    parser.add_argument("--short", type=int, default=2)
    parser.add_argument("--long", type=int, default=3)
    args = parser.parse_args()

    symbols = [args.symbol] if args.symbol else load_symbols_from_csv()
    os.makedirs("results/equity_curves", exist_ok=True)

    # Auto-clear failures.csv
    failures_path = "results/failures.csv"
    with open(failures_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Symbol", "Error"])

    # Run in parallel
    print(f"🚀 Running backtests on {len(symbols)} symbols using {min(cpu_count(), 4)} cores...")
    with Pool(processes=min(cpu_count(), 4)) as pool:
        results = pool.map(run_single_backtest, symbols)

    # Split successes and failures
    summary = [r for r in results if "Error" not in r]
    failures = [r for r in results if "Error" in r]

    if summary:
        pd.DataFrame(summary).to_csv("results/summary.csv", index=False)
        print("✅ Summary saved to results/summary.csv")

    if failures:
        with open(failures_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Symbol", "Error"])
            for row in failures:
                writer.writerow(row)
        print("⚠️ Failures saved to results/failures.csv")

if __name__ == "__main__":
    main()
