import yfinance as yf

# Solana USD Price
symbol = "SOL-USD"
start_date = "2022-01-01"
end_date = "2025-05-01"

# 🛠 Download data
df = yf.download(symbol, start=start_date, end=end_date)

# 💾 Save to CSV
df.to_csv("data/historical.csv", index-TRUE)
print(f"✅ Saved {symbol} data to data/historical.csv")
