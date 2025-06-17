
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
        start_equity = 100000
        cerebro.broker.set_cash(start_equity)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

        results = cerebro.run()
        strat = results[0]

        end_equity = cerebro.broker.getvalue()
        percent_return = ((end_equity - start_equity) / start_equity) * 100

        trades = strat.analyzers.trades.get_analysis()
        total_trades = trades.total.total if trades.total and trades.total.total else 0
        win_trades = trades.won.total if trades.won and trades.won.total else 0
        win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0

        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get("sharperatio", 0)

        drawdown = strat.analyzers.drawdown.get_analysis()
        max_drawdown = drawdown.get("max", {}).get("drawdown", 0)

        metrics = {
            "Start Equity": round(start_equity, 2),
            "End Equity": round(end_equity, 2),
            "Percent Return": round(percent_return, 2),
            "Total Trades": total_trades,
            "Win Rate": round(win_rate, 2),
            "Sharpe Ratio": round(sharpe_ratio, 2),
            "Max Drawdown": round(max_drawdown, 2)
        }

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        print("📈 Final Portfolio Value:", end_equity)
        print("📊 Metrics:", metrics)

        return results, metrics

    except Exception as e:
        print(f"❌ Error during backtest of {symbol}: {e}")
        return None, {}
