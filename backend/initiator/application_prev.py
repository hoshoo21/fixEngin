from dataclasses import asdict
import sys
import quickfix as fix
import time
import logging
from datetime import datetime
from initiator.model.logger import setup_logger
from order_manager.types import OrderRequest

__SOH__ = chr(1)
# Logger
setup_logger('initiator', 'Logs/initiator-message.log')
logfix = logging.getLogger('initiator')
class Application(fix.Application):
    ClOrdID = 0
    def __init__(self, on_exec_report_callback=None):
        
        super().__init__()
        #self.on_exec_report_callback = on_exec_report_callback
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
        # parse header
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        if msg_type.getValue() == fix.MsgType_ExecutionReport:
            report = {
            "orderId": message.getField(fix.OrderID().getTag()),
            "clOrdID": message.getField(fix.ClOrdID().getTag()),
            "symbol": message.getField(fix.Symbol().getTag()),
            "side": message.getField(fix.Side().getTag()),
            "orderQty": message.getField(fix.OrderQty().getTag()),
            "price": message.getField(fix.Price().getTag()),
            "execType": message.getField(fix.ExecType().getTag()),
            "ordStatus": message.getField(fix.OrdStatus().getTag())
            }
            if self.on_exec_report_call_back:
                try:
                    self.on_exec_report_call_back(report)
                except Exception as e:
                    print("Exec report callback failed:", e)

            self.onMessage(message, sessionID)
            return

    def genClOrdID(self):
        self.ClOrdID += 1
        return str(self.ClOrdID).zfill(5)


    
    def onMessage(self, message, sessionID):
        print(message)
        """Processing application message here"""
        pass
    def send_order(self, order_data: OrderRequest):
        try:
            message = fix.Message()
            header = message.getHeader()

            header.setField(fix.MsgType(fix.MsgType_NewOrderSingle)) #39 = D 

            message.setField(fix.ClOrdID(self.genClOrdID())) #11 = Unique Sequence Number
            message.setField(fix.Side(fix.Side_BUY)) #43 = 1 BUY 
            message.setField(fix.Symbol("MSFT")) #55 = MSFT
            message.setField(fix.OrderQty(10000)) #38 = 1000
            message.setField(fix.Price(100))
            message.setField(fix.OrdType(fix.OrdType_LIMIT)) #40=2 Limit Order 
            message.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION)) #21 = 3
            message.setField(fix.TimeInForce('0'))
            #message.setField(fix.Text("NewOrderSingle"))
            trstime = fix.TransactTime()
            trstime.setString(datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
            message.setField(trstime)

            fix.Session.sendToTarget(message, self.sessionID)
        except Exception as e:
            print("Application Order send failed:", e)
          
