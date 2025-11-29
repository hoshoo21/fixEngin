from abc import ABC, abstractmethod
from order_manager.types import OrderRequest

class Strategy(ABC):
    def __init__(self, symbol: str, order_manager=None):
        self.symbol = symbol
        self.order_manager = order_manager

    @abstractmethod
    def start(self):
        """Run the strategy (sync or spawn tasks)."""
        raise NotImplementedError
