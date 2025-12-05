import uuid, time
from .base import Strategy
from order_manager.types import OrderRequest

class MeanReversionStrategy(Strategy):
    def __init__(self, symbol, lookback=10, threshold=0.02, order_manager=None):
        super().__init__(symbol, order_manager)
        self.lookback = lookback
        self.threshold = threshold

    def start(self):
        # placeholder: in real life you'd read market data stream
        prices = [100, 101, 100.5, 99.8, 100.2]  # example
        mean = sum(prices[-self.lookback:]) / len(prices)
        last = prices[-1]
        diff = (mean - last) / mean
        if diff > self.threshold:
            # price is below mean -> buy
            order = OrderRequest(
                client_order_id=str(uuid.uuid4())[:8],
                symbol=self.symbol,
                side='BUY',
                quantity=100,
                order_type='MARKET',
                price=None,
                tif='DAY',
                algo='meanrev'
            )
            self.order_manager.submit(order)
        elif diff < -self.threshold:
            order = OrderRequest(
                client_order_id=str(uuid.uuid4())[:8],
                symbol=self.symbol,
                side='SELL',
                quantity=100,
                order_type='MARKET',
                price=None,
                tif='DAY',
                algo='meanrev'
            )
            self.order_manager.submit(order)
