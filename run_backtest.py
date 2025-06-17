import os
import pandas as pd
import backtrader as bt
from datetime import datetime

def run_backtest(symbol: str, strategy_class, strategy_name: str, save_path=None, **kwargs):
    safe_symbol = symbol.replace("-", "_").replace("/", "_")
    data_path = f"data/historical_{safe_symbol}.csv"

    if save_path is None:
        save_path = f"results/equity_curve_{safe_symbol}_{strategy_name}.csv"

    print(f"📊 Running Backtrader backtest for {symbol} using {strategy_name} strategy...")

    try:
        # Load data
        df = pd.read_csv(data_path, parse_dates=["Date"])
        df = df.rename(columns=str.lower)  # Backtrader prefers lowercase
        df = df.set_index("date")

        # Create Backtrader data feed
        data = bt.feeds.PandasData(dataname=df)

        # Initialize Backtrader engine
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class, **kwargs)
        cerebro.adddata(data)
        cerebro.broker.set_cash(100000)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        results = cerebro.run()
        strat = results[0]

        # Print metrics
        print("📈 Final Portfolio Value:", cerebro.broker.getvalue())
        print("📊 Sharpe Ratio:", strat.analyzers.sharpe.get_analysis())
        print("📊 Trade Analysis:", strat.analyzers.trades.get_analysis())

        # Optional: save performance curve (requires some custom logic)
        cerebro.plot()

        return results

    except Exception as e:
        print(f"❌ Error during backtest of {symbol}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    import argparse
    from strategies.pnshoot_strategy import PNShoot

    strategy_map = {
        "pnshoot": PNShoot
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", type=str, required=True)
    parser.add_argument("--symbol", type=str, required=True)
    parser.add_argument("--start", type=str, required=True)
    parser.add_argument("--end", type=str, required=True)
    args = parser.parse_args()

    run_backtest(
        symbol=args.symbol,
        strategy_class=strategy_map[args.strategy],
        strategy_name=args.strategy,
        start=args.start,
        end=args.end
    )
