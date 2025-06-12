import os
import plotly.express as px
import pandas as pd
from .utils import load_csv, safe_symbol

def plot_equity_curve(file_path, strategy="sma_crossover", save=False, output_dir="figures"):
    df = load_csv(file_path)
    symbol = os.path.basename(file_path).replace(".csv", "")

    fig = px.line(df, x="Date", y="Equity", title=f"Equity Curve - {symbol} ({strategy})")
    fig.update_layout(template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        fig.write_image(f"{output_dir}/equity_curve_{safe_symbol(symbol)}_{strategy}.png")
    fig.show()

def plot_top_n_equity_curves(n=5, strategy="sma_crossover", save=False, output_dir="figures"):
    summary_path = f"results/summary_{strategy}.csv"
    if not os.path.exists(summary_path):
        print(f"❌ {summary_path} not found.")
        return

    summary = pd.read_csv(summary_path)
    top_symbols = summary.sort_values("Percent Return", ascending=False).head(n)["Symbol"]

    fig = None
    for symbol in top_symbols:
        curve_path = f"results/equity_curves/{safe_symbol}.csv"
        if os.path.exists(curve_path):
            df = pd.read_csv(curve_path, parse_dates=["Date"])
            if fig is None:
                fig = px.line(df, x="Date", y="Equity", labels={"Equity": "Equity ($)"}, title=f"Top {n} Equity Curves ({strategy})")
                fig.update_traces(name=symbol, selector=dict(name='Equity'))
            else:
                fig.add_scatter(x=df["Date"], y=df["Equity"], mode="lines", name=symbol)

    if fig:
        fig.update_layout(template="plotly_white")

        if save:
            os.makedirs(output_dir, exist_ok=True)
            save_path = f"{output_dir}/top_{n}_equity_curves_{strategy}.png"
            fig.write_image(save_path)
            print(f"📸 Saved Plotly figure to {save_path}")

        fig.show()
