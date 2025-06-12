import os
import plotly.express as px
from .utils import load_csv

def plot_summary_bar(csv_file="results/summary_sma_crossover.csv", metric="Percent Return", save=False, output_dir="figures"):
    df = load_csv(csv_file)
    df = df.sort_values(metric, ascending=False)

    fig = px.bar(df, x="Symbol", y=metric, title=f"{metric} by Symbol", labels={metric: metric})
    fig.update_layout(xaxis_tickangle=-45, template="plotly_white")

    if save:
        os.makedirs(output_dir, exist_ok=True)
        fig.write_image(f"{output_dir}/summary_{metric.replace(' ', '_')}.png")
    fig.show()
