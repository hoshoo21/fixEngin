# order_manager/types.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class OrderRequest:
    client_order_id: str
    symbol: str
    side: str           # 'BUY'|'SELL'
    quantity: float
    order_type: str     # 'MARKET'|'LIMIT'|'STOP'
    price: Optional[float] = None
    tif: str = "DAY"    # 'DAY'|'GTC'|'IOC'
    algo: Optional[str] = None
    meta: dict = None
