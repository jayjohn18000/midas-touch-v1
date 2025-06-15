import backtrader as bt

class pNshoot(bt.Strategy):
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
        # Indicators
        self.sma_fast = bt.indicators.SMA(self.data.close, period=self.p.fast_period)
        self.sma_slow = bt.indicators.SMA(self.data.close, period=self.p.slow_period)
        self.adx = bt.indicators.ADX(self.data, period=self.p.adx_period)
        self.atr = bt.indicators.ATR(self.data, period=self.p.atr_period)
        self.volume_sma = bt.indicators.SMA(self.data.volume, period=self.p.volume_period)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if self.position:
            # Optional exit conditions: Crossover reversal or ADX weakness
            if self.crossover < 0 or self.adx[0] < 20:
                self.close()
            return

        # Long entry condition
        if (self.crossover > 0 and 
            self.adx[0] > self.p.adx_threshold and 
            self.data.volume[0] > self.volume_sma[0]):
            self.buy()

        # Short entry condition
        elif (self.crossover < 0 and 
              self.adx[0] > self.p.adx_threshold and 
              self.data.volume[0] > self.volume_sma[0]):
            self.sell()

# Save to file
file_path = "/mnt/data/pnshoot_strategy.py"
with open(file_path, "w") as f:
    f.write(pnshoot_code)

file_path
