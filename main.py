import argparse
import os
import pandas as pd
from fetch_data import fetch_data
from run_backtest import run_backtest
from strategies.sma_crossover import sma_crossover_strategy
import re
from data.soapy_symbols import clean_crypto_pairs, clean_crypto_public, clean_quant_public

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
    summary = []

    for symbol in symbols:
        try:
            print(f"📈 Processing {symbol}...")
            df = fetch_data(symbol, start_date=args.start, end_date=args.end)

            # ✅ Skip symbol if data fetch failed or is invalid
            if df is None:
                print(f"⚠️ Skipping {symbol} due to missing or invalid data.")
                continue

            strategy_fn = strategy_map[args.strategy]
            result_df = run_backtest(
                symbol=symbol,
                strategy_fn=strategy_fn,
                strategy_name=args.strategy,
                short=args.short,
                long=args.long,
                save_path=f"results/equity_curves/{symbol}.csv"
            )
            if result_df.empty or 'Equity' not in result_df.columns:
                print(f"⚠️ Skipping {symbol} — no valid backtest results.")
                continue

            final_equity = result_df['Equity'].iloc[-1]
            start_equity = result_df['Equity'].iloc[0]
            pct_return = round((final_equity - start_equity) / start_equity * 100, 2)

            summary.append({
                "Symbol": symbol,
                "Strategy": args.strategy,
                "Final Equity": round(final_equity, 2),
                "Percent Return": pct_return
            })

        except Exception as e:
            print(f"❌ Error on {symbol}: {e}")

    if summary:
        pd.DataFrame(summary).to_csv("results/summary.csv", index=False)
        print("✅ Summary saved to results/summary.csv")

if __name__ == "__main__":
    main()
