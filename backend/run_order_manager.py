from order_manager.adapters.fix_initiator import FIXInitiatorWrapper
from backend.initiator.application_prev import Application as FIXApp
from order_manager.manager import OrderManager

fix_wrapper = FIXInitiatorWrapper(config_file='client.cfg', app_class=FIXApp)
fix_wrapper.start()

om = OrderManager(fix_wrapper)

# Example: run a TWAP
from order_manager.strategies.twap import TWAPStrategy
tw = TWAPStrategy(symbol="MSFT", side="BUY", total_qty=1000, slices=4, interval_sec=5, order_manager=om)
tw.start()



