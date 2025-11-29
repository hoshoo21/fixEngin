import quickfix as fix
import logging
import time
from model.logger import setup_logger

__SOH__ = chr(1)

# Setup logger
setup_logger('acceptor', 'Logs/acceptor-message.log')
logfix = logging.getLogger('acceptor')

class Application(fix.Application):
    """Generic FIX Application / Acceptor"""
    orderID = 0
    execID = 0

    def onCreate(self, sessionID):
        logfix.info("onCreate : Session (%s)" % sessionID.toString())

    def onLogon(self, sessionID):
        self.sessionID = sessionID
        logfix.info("Successful Logon to session '%s'." % sessionID.toString())

    def onLogout(self, sessionID):
        logfix.info("Session (%s) logout !" % sessionID.toString())

    def toAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(Admin) S >> %s" % msg)

    def fromAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(Admin) R << %s" % msg)

    def toApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(App) S >> %s" % msg)

    def fromApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(App) R << %s" % msg)
        self.onMessage(message, sessionID)

    def onMessage(self, message, sessionID):
        """Process NewOrderSingle messages generically"""
        # Extract standard fields
        beginString = fix.BeginString()
        msgType = fix.MsgType()
        message.getHeader().getField(beginString)
        message.getHeader().getField(msgType)

        symbol = fix.Symbol()
        side = fix.Side()
        ordType = fix.OrdType()
        orderQty = fix.OrderQty()
        price = fix.Price()
        clOrdID = fix.ClOrdID()

        # Get fields safely
        message.getField(ordType)
        message.getField(symbol)
        message.getField(side)
        message.getField(orderQty)
        message.getField(clOrdID)

        # Price is only required for LIMIT or STOP orders
        if ordType.getValue() in (fix.OrdType_LIMIT, fix.OrdType_STOP):
            message.getField(price)
        else:
            price.setValue(0)  # MARKET orders: price not required

        # Log received order
        logfix.info(f"Received order: OrdType={ordType.getValue()}, Side={side.getValue()}, Symbol={symbol.getValue()}, Qty={orderQty.getValue()}, Price={price.getValue()}")

        # Build execution report
        executionReport = fix.Message()
        executionReport.getHeader().setField(beginString)
        executionReport.getHeader().setField(fix.MsgType(fix.MsgType_ExecutionReport))

        executionReport.setField(fix.OrderID(self.genOrderID()))
        executionReport.setField(fix.ExecID(self.genExecID()))
        executionReport.setField(fix.OrdStatus(fix.OrdStatus_FILLED))
        executionReport.setField(symbol)
        executionReport.setField(side)
        executionReport.setField(fix.CumQty(orderQty.getValue()))
        executionReport.setField(fix.LastShares(orderQty.getValue()))
        executionReport.setField(clOrdID)
        executionReport.setField(orderQty)

        # Set executed price
        executionReport.setField(fix.AvgPx(price.getValue()))
        executionReport.setField(fix.LastPx(price.getValue()))

        # Optional fields depending on FIX version
        if beginString.getValue() >= fix.BeginString_FIX41:
            executionReport.setField(fix.ExecType(fix.ExecType_FILL))
            executionReport.setField(fix.LeavesQty(0))

        # Send execution report
        try:
            fix.Session.sendToTarget(executionReport, sessionID)
            logfix.info(f"Execution report sent for ClOrdID={clOrdID.getValue()}")
        except fix.SessionNotFound as e:
            logfix.error("Session not found: %s" % e)

    def genOrderID(self):
        self.orderID += 1
        return str(self.orderID).zfill(5)

    def genExecID(self):
        self.execID += 1
        return str(self.execID).zfill(5)

    def run(self):
        while True:
            time.sleep(2)
