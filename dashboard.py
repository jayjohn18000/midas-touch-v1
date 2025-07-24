import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

RESULTS_DIR = "results"

st.set_page_config(layout="wide")
st.title("📈 Strategy Comparison Dashboard")

# Load all strategy summaries
summary_all_path = os.path.join(RESULTS_DIR, "summary_all.csv")

if not os.path.exists(summary_all_path):
    st.error("summary_all.csv not found. Run backtests first.")
    st.stop()

df = pd.read_csv(summary_all_path)

# --- Sidebar selections
symbols = sorted(df["Symbol"].unique())
strategies = sorted(df["Strategy"].unique())

selected_symbols = st.sidebar.multiselect("Select Symbols", symbols, default=symbols[:3])
selected_strategies = st.sidebar.multiselect("Select Strategies", strategies, default=strategies)

# --- Filter DataFrame
filtered = df[df["Symbol"].isin(selected_symbols) & df["Strategy"].isin(selected_strategies)]

if filtered.empty:
    st.warning("No results found for selected filters.")
    st.stop()

# --- Table of Metrics
st.subheader("📊 Strategy Metrics Comparison")
st.dataframe(filtered.style.format(precision=2))

# --- Plotting comparison
selected_metric = st.selectbox("Select Metric to Compare", 
    ["Percent Return", "Sharpe Ratio", "Max Drawdown", "Total Trades", "Win Rate"])

fig, ax = plt.subplots(figsize=(10, 6))
for strategy in selected_strategies:
    strat_data = filtered[filtered["Strategy"] == strategy]
    ax.plot(strat_data["Symbol"], strat_data[selected_metric], label=strategy, marker="o")

ax.set_title(f"{selected_metric} Comparison")
ax.set_ylabel(selected_metric)
ax.set_xticklabels(selected_symbols, rotation=45)
ax.legend()
st.pyplot(fig)
