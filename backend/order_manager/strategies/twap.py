# order_manager/strategies/twap.py
import time
import uuid
from .base import Strategy
from order_manager.types import OrderRequest

class TWAPStrategy(Strategy):
    def __init__(self, symbol, side, total_qty, slices, interval_sec, order_manager):
        super().__init__(symbol, order_manager)
        self.side = side
        self.total_qty = total_qty
        self.slices = slices
        self.interval_sec = interval_sec

    def start(self):
        slice_qty = int(self.total_qty / self.slices)
        remainder = int(self.total_qty - slice_qty * self.slices)
        for i in range(self.slices):
            qty = slice_qty + (1 if i == self.slices - 1 and remainder else 0)
            order = OrderRequest(
                client_order_id = str(uuid.uuid4())[:10],
                symbol = self.symbol,
                side = self.side,
                quantity = qty,
                order_type = 'LIMIT',   # or MARKET depending on strategy
                price = None,           # you may set price based on market
                tif = 'DAY',
                algo = 'twap'
            )
            print(order.order_type)
            self.order_manager.submit(order)
            time.sleep(self.interval_sec)
