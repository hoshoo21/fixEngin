import sys
import quickfix as fix
import time
import logging
from datetime import datetime
from initiator.model.logger import setup_logger


__SOH__ = chr(1)
# Logger
setup_logger('initiator', 'Logs/initiator-message.log')
logfix = logging.getLogger('initiator')
class Application(fix.Application):
    ClOrdID = 0
    def __init__(self, on_exec_report_callback=None):
        super().__init__()
        self.on_exec_report_callback = on_exec_report_callback
    def onCreate(self, sessionID):
        print("onCreate : Session (%s)" % sessionID.toString())
        return

    def onLogon(self, sessionID):
        self.sessionID = sessionID
        print("Successful Logon to session '%s'." % sessionID.toString())
        return

    def onLogout(self, sessionID):
        print("Session (%s) logout !" % sessionID.toString())
        return

    def toAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(Admin) S >> %s" % msg)
        return
    def fromAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(Admin) R << %s" % msg)
        return
    def toApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(App) S >> %s" % msg)
        return
    def fromApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(App) R << %s" % msg)
        self.onMessage(message, sessionID)
        return

    def genClOrdID(self):
        self.ClOrdID += 1
        return str(self.ClOrdID).zfill(5)


    
    def onMessage(self, message, sessionID):
        print(message)
        """Processing application message here"""
        pass
    def send_order(self, order: dict):
        # Ensure session is ready
        if not hasattr(self, "sessionID") or self.sessionID is None:
            print("Session not ready. Cannot send order.")
            return

        message = fix.Message()
        header = message.getHeader()

        # Header
        header.setField(fix.BeginString("FIX.4.3"))
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        header.setField(fix.SenderCompID("CLIENT"))
        header.setField(fix.TargetCompID("SERVER"))
        header.setField(fix.SendingTime())

        # Required fields
        message.setField(fix.ClOrdID(self.genClOrdID()))
        
        # Side: BUY/SELL
        side_map = {'BUY': fix.Side_BUY, 'SELL': fix.Side_SELL}
        side_value = side_map.get(order.get('side', 'BUY'))
        message.setField(fix.Side(side_value))

        # Symbol
        message.setField(fix.Symbol(order.get('symbol', 'MSFT')))

        # Order quantity
        message.setField(fix.OrderQty(int(order.get('quantity', 1))))

        # Handling instruction
        message.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))

        # Order type
        ord_type_map = {
            'MARKET': fix.OrdType_MARKET,
            'LIMIT': fix.OrdType_LIMIT,
            'STOP': fix.OrdType_STOP
        }
        ord_type_value = ord_type_map.get(order.get('ordertype', 'LIMIT'))
        message.setField(fix.OrdType(ord_type_value))

        # Price only for LIMIT or STOP
        if ord_type_value in (fix.OrdType_LIMIT, fix.OrdType_STOP):
            price = float(order.get('price', 0))
            message.setField(fix.Price(price))

        # Time in force
        tif_map = {'DAY': fix.TimeInForce_DAY, 'GTC': fix.TimeInForce_GOOD_TILL_CANCEL, 'IOC': fix.TimeInForce_IMMEDIATE_OR_CANCEL}
        tif_value = tif_map.get(order.get('tif', 'DAY'))
        message.setField(fix.TimeInForce(tif_value))

        # Text / Notes
        text = order.get('notes', 'NewOrderSingle')
        clean_text = ''.join(c for c in text.strip()[:255] if 32 <= ord(c) <= 126)
        message.setField(fix.Text(clean_text))

        # Transaction time
        trstime = fix.TransactTime()
        trstime.setString(datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
        message.setField(trstime)

        # Debug print of message being sent
        print("Sending message:")
        print(message.toString().replace('\x01', '|'))

        # Send message
        fix.Session.sendToTarget(message, self.sessionID)
