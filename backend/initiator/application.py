#!/usr/bin/python
# -*- coding: utf8 -*-
"""FIX Application"""
import sys
from order_manager.types import OrderRequest
import quickfix as fix
import time
import logging
from datetime import datetime
from initiator.model.logger import setup_logger
__SOH__ = chr(1)

# Logger
setup_logger('initiator', 'Logs/initiator-message.log')
logfix = logging.getLogger('initiator')


class Application(fix.Application,):
    """FIX Application"""
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
    def onMessage_ExecutionReport(self, message, sessionID):

        def get_optional(tag):
            try:
                return message.getField(tag)
            except:
                return None

        report = {
            "orderId":  get_optional(fix.OrderID().getTag()),
            "clOrdID":  get_optional(fix.ClOrdID().getTag()),
            "symbol":   get_optional(fix.Symbol().getTag()),
            "side":     get_optional(fix.Side().getTag()),
            "orderQty": get_optional(fix.OrderQty().getTag()),
            "price":    get_optional(fix.Price().getTag()),
            "execType": get_optional(fix.ExecType().getTag()),
            "ordStatus":get_optional(fix.OrdStatus().getTag())
        }

        print("Execution Report Parsed: ", report)

        if self.on_exec_report_callback:
            self.on_exec_report_callback(report)
    def fromApp(self, message, sessionID):
        print("RAW ER:", message.toString().replace("\x01", "|"))
        self.print_message(message)
    def print_message(self,msg):
        msg_str = ''
        msg_type = self.get_field_value(fix.MsgType(), msg.getHeader())
        if msg_type == fix.MsgType_News:
            msg_str = "MessageType=News, Sender="
            msg_str += self.get_field_value(fix.SenderCompID(), msg.getHeader())
            msg_str += ", HeadLine="
            msg_str += self.get_field_value(fix.Headline(), msg)
            msg_str += ", Text="
            msg_str += self.get_field_value(fix.Text(), msg)
        elif msg_type == fix.MsgType_MarketDataRequestReject:
            print("REJECTED")
        elif msg_type == fix.MsgType_MarketDataSnapshotFullRefresh:
            print("SNAPSHOT")
            print(self.get_field_value(fix.Symbol(), msg))
            print(msg)
            
        else:
            msg_str = "OrderID="
            msg_str += self.get_field_value(fix.ClOrdID(), msg)
            msg_str += ", MessageType="
            msg_str += self.get_message_type(msg)
            msg_str += ", OrderStatus=" #39
            msg_str += self.get_order_status(msg)
            msg_str += ", Sender="
            msg_str += self.get_field_value(fix.SenderCompID(), msg.getHeader())
            msg_str += ", Target="
            msg_str += self.get_field_value(fix.TargetCompID(), msg.getHeader())
            msg_str += ", OrderType=" #40 1-Market, 2-Limit
            msg_str += self.get_order_type(msg)
            msg_str += ", Side=" #54 1-Buy,2-Sell
            msg_str += 'BUY' if self.get_field_value(fix.Side(), msg) == fix.Side_BUY else 'SELL'
            msg_str += ", Quantity=" #38
            msg_str += str(self.get_field_value(fix.OrderQty(), msg))
            msg_str += ", Price="
            msg_str += str(self.get_field_value(fix.Price(), msg))
            msg_str += ", Symbol="
            msg_str += self.get_field_value(fix.Symbol(), msg)
            msg_str += ", ExecutionType=" #150
            msg_str += self.get_exec_type(msg)
            if msg.isSetField(fix.Text().getField()):
                msg_str += ", Text="
                msg_str += self.get_field_value(fix.Text(), msg)
            msg_str += ", ExecutedQuantity=" #14
            msg_str += str(self.get_field_value(fix.CumQty(), msg))

        print(msg_str)
    def get_message_type(self,msg) :
        msg_type = self.get_field_value(fix.MsgType(), msg.getHeader())
        if msg_type == fix.MsgType_ExecutionReport:
            return "ExecutionReport"
        elif msg_type == fix.MsgType_News:
            return "News"
        elif msg_type == fix.MsgType_NewOrderSingle:
            return "NewOrderSingle"
        else:
            return msg_type

    def get_field_value(self, fobj, msg):
        if msg.isSetField(fobj.getField()):
            msg.getField(fobj)
            return fobj.getValue()
        else:
            return "None"
    def get_order_type(self,msg):
        ord_type = self.get_field_value(fix.OrdType(), msg)
        if ord_type == fix.OrdType_LIMIT:
            return "LIMIT"
        elif ord_type == fix.OrdType_MARKET:
            return "MARKET"
        else:
            return ord_type

    def get_exec_type(self,msg):
        rpt = self.get_field_value(fix.ExecType(), msg)
        if rpt == fix.ExecType_NEW:
            return "NEW"
        elif rpt == fix.ExecType_REJECTED:
            return "REJECTED"
        elif rpt == fix.ExecType_TRADE:
            print ("execution type Trade")
            return "FILLED"
        elif rpt == fix.ExecType_CANCELED:
            return "CANCELED"
        else:
           
            return rpt


    def get_order_status(self,msg):
        status = self.get_field_value(fix.OrdStatus(), msg)
        if status == fix.OrdStatus_NEW:
            return "NEW"
        elif status == fix.OrdStatus_FILLED:
            return "FILLED"
        elif status == fix.OrdStatus_REJECTED:
            return "REJECTED"
        elif status == fix.OrdStatus_CANCELED:
            return "CANCELED"
        else:
            return status
        #self.creck(message,sessionID)
        
        # msg = message.toString().replace(__SOH__, "|")
        # logfix.info("(App) R << %s" % msg)
        # self.onMessage(message, sessionID)
        # msg_type = fix.MsgType()
        # message.getHeader().getField(msg_type)
        # if msg_type.getValue() == fix.MsgType_ExecutionReport:
        #     report = {
        #     "orderId": message.getField(fix.OrderID().getTag()),
        #     "clOrdID": message.getField(fix.ClOrdID().getTag()),
        #     "symbol": message.getField(fix.Symbol().getTag()),
        #     "side": message.getField(fix.Side().getTag()),
        #     "orderQty": message.getField(fix.OrderQty().getTag()),
        #     "price": message.getField(fix.Price().getTag()),
        #     "execType": message.getField(fix.ExecType().getTag()),
        #     "ordStatus": message.getField(fix.OrdStatus().getTag())
        #     }
        #     if self.on_exec_report_call_back:
        #         try:
        #             self.on_exec_report_call_back(report)
        #         except Exception as e:
        #             print("Exec report callback failed:", e)

        #     #self.onMessage(message, sessionID)
        #     return

        return

    def onMessage(self, message, sessionID):
        """Processing application message here"""
        pass

    def genClOrdID(self):
        """Generate ClOrdID"""
        self.ClOrdID += 1
        return str(self.ClOrdID).zfill(5)

    def send_order(self, Order:OrderRequest):
        """Request sample new order single"""
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
        message.setField(fix.Text("NewOrderSingle"))
        trstime = fix.TransactTime()
        trstime.setString(datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")[:-3])
        message.setField(trstime)

        fix.Session.sendToTarget(message, self.sessionID)

    def run(self):
        """Run"""
        while 1:
            options = str(input("Please choose 1 for Put New Order or 2 for Exit!\n"))
            if options == '1':
                self.put_new_order()
                print("Done: Put New Order\n")
                continue
            if  options == '2':
                sys.exit(0)
            else:
                print("Valid input is 1 for order, 2 for exit\n")
            time.sleep(2)