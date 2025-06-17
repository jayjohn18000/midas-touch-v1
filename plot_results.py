
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_equity_curve(symbol, strategy):
    filepath = f"results/equity_curves/{strategy}/{symbol}.csv"
    if not os.path.exists(filepath):
        print(f"❌ Equity curve not found for {symbol} [{strategy}]")
        return
    df = pd.read_csv(filepath)
    if "Equity" not in df.columns:
        print(f"❌ 'Equity' column missing in {filepath}")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["Equity"], label=f"{symbol} - {strategy}")
    plt.title(f"Equity Curve: {symbol} ({strategy})")
    plt.xlabel("Time Step")
    plt.ylabel("Portfolio Value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_summary_metric(metric="Percent Return", strategy=None):
    summary_path = "results/summary_all.csv"
    if not os.path.exists(summary_path):
        print("❌ summary_all.csv not found")
        return
    df = pd.read_csv(summary_path)
    if strategy:
        df = df[df["Strategy"] == strategy]

    if metric not in df.columns:
        print(f"❌ Metric '{metric}' not found in summary_all.csv")
        return

    df_sorted = df.sort_values(metric, ascending=False)
    plt.figure(figsize=(12, 6))
    plt.bar(df_sorted["Symbol"], df_sorted[metric], color="skyblue")
    plt.title(f"{metric} by Symbol" + (f" ({strategy})" if strategy else ""))
    plt.xlabel("Symbol")
    plt.ylabel(metric)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Plot backtest results")
    parser.add_argument("--symbol", help="Symbol to plot equity curve for")
    parser.add_argument("--strategy", help="Strategy used for that symbol")
    parser.add_argument("--metric", help="Summary metric to plot across symbols")
    args = parser.parse_args()

    if args.symbol and args.strategy:
        plot_equity_curve(args.symbol, args.strategy)
    elif args.metric:
        plot_summary_metric(metric=args.metric, strategy=args.strategy)
    else:
        print("⚠️ Please provide either --symbol and --strategy, or --metric [--strategy]")

if __name__ == "__main__":
    main()
