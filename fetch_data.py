import yfinance as yf
import pandas as pd
import os

def fetch_data(symbol: str, start_date: str = "2022-01-01", end_date: str = "2025-05-01") -> pd.DataFrame | None:
    # Format safe file path
    safe_symbol = symbol.replace("-", "_").replace("/", "_")
    file_path = f"data/historical_{safe_symbol}.csv"

    # ✅ Step 1: Use cached file if it exists
    if os.path.exists(file_path):
        print(f"📂 Using cached data for {symbol} from {file_path}")
        try:
            df = pd.read_csv(file_path, parse_dates=["Date"])
            if df.empty or "Close" not in df.columns or df["Close"].isna().all():
                print(f"⚠️ Cached file invalid or incomplete for {symbol}, re-downloading...")
            else:
                return df
        except Exception as e:
            print(f"⚠️ Failed to load cached data for {symbol}: {e}, re-downloading...")

    # 📥 Step 2: Download fresh data if no valid cache
    print(f"📥 Downloading data for {symbol} from {start_date} to {end_date}...")

    try:
        df = yf.download(symbol, start=start_date, end=end_date, group_by="ticker")

        if df.empty:
            print(f"⚠️ No data found for {symbol}")
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)

        df = df.drop(columns=["Adj Close"], errors="ignore")
        df.reset_index(inplace=True)
        df.index.name = "Index"

        if "Close" not in df.columns or df["Close"].isna().all():
            print(f"⚠️ Close prices missing or invalid for {symbol}")
            return None

        os.makedirs("data", exist_ok=True)
        df.to_csv(file_path, index=False)

        print(f"✅ Saved {symbol} data to {file_path}")
        return df

    except Exception as e:
        print(f"❌ Failed to fetch {symbol}: {e}")
        return None
