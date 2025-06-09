import yfinance as yf
import pandas as pd
import os

def fetch_data(symbol: str, start_date: str = "2022-01-01", end_date: str = "2025-05-01") -> pd.DataFrame | None:
    print(f"📥 Downloading data for {symbol} from {start_date} to {end_date}...")

    try:
        df = yf.download(symbol, start=start_date, end=end_date, group_by="ticker")

        # Early exit if no data
        if df.empty:
            print(f"⚠️ No data found for {symbol}")
            return None

        # Flatten MultiIndex columns if needed
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)

        # Drop 'Adj Close' if it exists
        df = df.drop(columns=["Adj Close"], errors="ignore")

        # Ensure clean date index
        df.reset_index(inplace=True)
        df.index.name = "Index"

        # Optional: validate if price data is valid
        if "Close" not in df.columns or df["Close"].isna().all():
            print(f"⚠️ Close prices missing or invalid for {symbol}")
            return None

        # Save file
        safe_symbol = symbol.replace("-", "_").replace("/", "_")
        os.makedirs("data", exist_ok=True)
        file_path = f"data/historical_{safe_symbol}.csv"
        df.to_csv(file_path, index=False)

        print(f"✅ Saved {symbol} data to {file_path}")
        return df

    except Exception as e:
        print(f"❌ Failed to fetch {symbol}: {e}")
        return None
