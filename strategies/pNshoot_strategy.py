
import backtrader as bt

class PNShoot(bt.Strategy):
    params = dict(
        fast_period=20,
        slow_period=50,
        adx_period=14,
        atr_period=14,
        volume_period=20,
        adx_threshold=25,
        atr_mult=1.5,
        risk_reward=2.0
    )

    def __init__(self):
        self.order = None  # to keep track of pending orders
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.fast_period)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.slow_period)
        self.adx = bt.indicators.ADX(self.data, period=self.p.adx_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.volume_sma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def next(self):
        if self.order:
            return  # waiting for pending order

        if self.position:
            # Optional exit: if trend weakens or crossover reverses
            if self.crossover < 0 or self.adx[0] < 20:
                self.log(f'CLOSE: {self.data.close[0]}')
                self.order = self.close()
            return

        if self.crossover > 0 and self.adx[0] > self.p.adx_threshold and self.data.volume[0] > self.volume_sma[0]:
            self.log(f'BUY: {self.data.close[0]}')
            self.order = self.buy()

        elif self.crossover < 0 and self.adx[0] > self.p.adx_threshold and self.data.volume[0] > self.volume_sma[0]:
            self.log(f'SELL: {self.data.close[0]}')
            self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.log(f'ORDER EXECUTED at {order.executed.price}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = Nonea