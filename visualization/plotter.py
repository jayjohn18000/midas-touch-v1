import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_equity_curve(file_path, save=False, output_dir="figures"):
    df = pd.read_csv(file_path, parse_dates=["Date"])
    symbol = os.path.basename(file_path).replace(".csv", "")
    
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Equity"], label="Equity")
    plt.title(f"Equity Curve - {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.tight_layout()

    if save:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/equity_curve_{symbol}.png")
        print(f"📸 Saved plot to {output_dir}/equity_curve_{symbol}.png")

    plt.show()


def plot_summary_bar(csv_file="results/summary.csv", metric="Percent Return", save=False, output_dir="figures"):
    df = pd.read_csv(csv_file)
    df = df.sort_values(metric, ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(df["Symbol"], df[metric])
    plt.xticks(rotation=45, ha='right')
    plt.title(f"{metric} by Symbol")
    plt.xlabel("Symbol")
    plt.ylabel(metric)
    plt.tight_layout()

    if save:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/summary_{metric.replace(' ', '_')}.png")
        print(f"📸 Saved plot to {output_dir}/summary_{metric.replace(' ', '_')}.png")

    plt.show()


def plot_top_n_equity_curves(n=5, strategy="sma_crossover", save=False, output_dir="figures"):
    summary_path = "results/summary.csv"
    if not os.path.exists(summary_path):
        print("❌ summary.csv not found.")
        return

    summary = pd.read_csv(summary_path)
    top_symbols = summary.sort_values("Percent Return", ascending=False).head(n)["Symbol"]

    plt.figure(figsize=(12, 6))
    for symbol in top_symbols:
        curve_path = f"results/equity_curves/{symbol}.csv"
        if os.path.exists(curve_path):
            df = pd.read_csv(curve_path, parse_dates=["Date"])
            plt.plot(df["Date"], df["Equity"], label=symbol)

    plt.legend()
    plt.title(f"Top {n} Equity Curves ({strategy})")
    plt.xlabel("Date")
    plt.ylabel("Equity ($)")
    plt.grid(True)
    plt.tight_layout()

    if save:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/top_{n}_equity_curves_{strategy}.png")
        print(f"📸 Saved plot to {output_dir}/top_{n}_equity_curves_{strategy}.png")

    plt.show()
