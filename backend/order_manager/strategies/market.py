# order_manager/strategies/market.py
import time
from .base import Strategy
from order_manager.types import OrderRequest
import uuid

class MarketStrategy(Strategy):
    def __init__(self, symbol, side, qty, order_manager):
        super().__init__(symbol, order_manager)
        self.side = side
        self.qty = qty

    def start(self):
        order = OrderRequest(
            client_order_id = str(uuid.uuid4())[:8],
            symbol = self.symbol,
            side = self.side,
            quantity = self.qty,
            order_type = 'MARKET',
            price = None,
            tif = 'IOC',
            algo = 'market'
        )
        self.order_manager.submit(order)
