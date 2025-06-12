import os
import pandas as pd
import plotly.express as px


def plot_equity_curve(file_path, save=False, output_dir="figures"):
    df = pd.read_csv(file_path, parse_dates=["Date"])
    symbol = os.path.basename(file_path).replace(".csv", "")

    fig = px.line(df, x="Date", y="Equity", title=f"Equity Curve - {symbol}", labels={"Equity": "Equity ($)"})
    fig.update_layout(template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        save_path = f"{output_dir}/equity_curve_{symbol}.png"
        fig.write_image(save_path)
        fig.show()
        print(f"📸 Saved Plotly figure to {save_path}")

    fig.show()


def plot_summary_bar(csv_file="results/summary_all.csv", metric="Percent Return", save=False, output_dir="figures"):
    df = pd.read_csv(csv_file)
    df = df.sort_values(metric, ascending=False)

    fig = px.bar(df, x="Symbol", y=metric, title=f"{metric} by Symbol", labels={metric: metric})
    fig.update_layout(xaxis_tickangle=-45, template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        save_path = f"{output_dir}/summary_{metric.replace(' ', '_')}.png"
        fig.write_image(save_path)
        print(f"📸 Saved Plotly figure to {save_path}")

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
        curve_path = f"results/equity_curves/{symbol}.csv"
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
