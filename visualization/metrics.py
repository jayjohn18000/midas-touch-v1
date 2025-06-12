import os
import plotly.express as px
import pandas as pd
from utils import load_csv

def plot_metric_scatter(csv_file="results/summary_sma_crossover.csv", x_metric="Sharpe Ratio", y_metric="Percent Return", save=False, output_dir="figures"):
    df = load_csv(csv_file)

    fig = px.scatter(df, x=x_metric, y=y_metric, color="Symbol",
                     title=f"{y_metric} vs {x_metric}",
                     hover_data=["Symbol", "Win Rate", "Max Drawdown"])
    fig.update_layout(template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        fig.write_image(f"{output_dir}/scatter_{y_metric}_{x_metric}.png")
    fig.show()

def plot_sharpe_distribution(csv_file="results/summary_all.csv", save=False, output_dir="figures"):
    df = pd.read_csv(csv_file)
    fig = px.histogram(df, x="Sharpe Ratio", nbins=20,
                       title="Distribution of Sharpe Ratios",
                       labels={"Sharpe Ratio": "Sharpe Ratio"})
    fig.update_layout(template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/sharpe_distribution.png"
        fig.write_image(path)
        print(f"📸 Saved to {path}")

    fig.show()


def plot_drawdown_vs_return(csv_file="results/summary_all.csv", save=False, output_dir="figures"):
    df = pd.read_csv(csv_file)
    fig = px.scatter(df, x="Max Drawdown", y="Percent Return", color="Strategy",
                     title="Return vs Max Drawdown",
                     labels={"Max Drawdown": "Max Drawdown (%)", "Percent Return": "Percent Return (%)"})
    fig.update_layout(template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/return_vs_drawdown.png"
        fig.write_image(path)
        print(f"📸 Saved to {path}")

    fig.show()


def plot_winrate_bar(csv_file="results/summary_all.csv", save=False, output_dir="figures"):
    df = pd.read_csv(csv_file)
    df = df.sort_values("Win Rate", ascending=False)
    fig = px.bar(df, x="Symbol", y="Win Rate", color="Strategy",
                 title="Win Rate by Symbol",
                 labels={"Win Rate": "Win Rate (%)"})
    fig.update_layout(xaxis_tickangle=-45, template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        path = f"{output_dir}/win_rate_bar.png"
        fig.write_image(path)
        print(f"📸 Saved to {path}")

    fig.show()