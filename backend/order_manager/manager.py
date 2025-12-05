# order_manager/manager.py
import queue
import threading
import time
from order_manager.types import OrderRequest

class OrderManager:
    def __init__(self, fix_initiator, max_position=100000):
        self.fix = fix_initiator
        self.max_position = max_position
        self.order_queue = queue.Queue()
        
        self.positions = {}   # symbol -> signed qty
        threading.Thread(target=self._worker, daemon=True).start()

    def submit(self, order: OrderRequest):
        # basic validation
        if order.quantity <= 0:
            raise ValueError("Quantity must be > 0")
        # risk check: naive position limit per symbol
        pos = self.positions.get(order.symbol, 0)
        projected = pos + (order.quantity if order.side == 'BUY' else -order.quantity)
        if abs(projected) > self.max_position:
            raise RuntimeError("Position limit exceeded")
        self.order_queue.put(order)

    def _worker(self):
        while True:
            print (self.order_queue)
            if not (hasattr(self.order_queue, "get")):
                print ("no get method on queue")
                return
            order = self.order_queue.get()
            try:
                self._send(order)
            except Exception as e:
                print("Order send failed:", e)
            self.order_queue.task_done()

    def _send(self, order: OrderRequest):
        # send via FIX (blocking until sent or queued by FIXInitiator)
        self.fix.send_order(order)
        # we could track order state, map clOrdID -> order for cancels etc.
        print("Submitted order to FIX:", order)
