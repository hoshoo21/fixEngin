import quickfix as fix
import os, threading, time, json, pika

class FIXInitiatorWrapper:
    def __init__(self, config_file, app_class):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        cfg = os.path.join(BASE_DIR,config_file)
        self.settings = fix.SessionSettings(cfg)
        #self.application = app_class(on_exec_report_callback=self._on_exec_report)
        self.application = app_class()
        
        self.storefactory = fix.FileStoreFactory(self.settings)
        self.logfactory = fix.FileLogFactory(self.settings)
        self.initiator = fix.SocketInitiator(self.application, self.storefactory, self.settings, self.logfactory)
      
        self._rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self._rabbit_ch = self._rabbit_conn.channel()
        self._rabbit_ch.queue_declare(queue='execution_reports', durable=True)

    def start(self):
        self.initiator.start()
        # don't block; SocketInitiator runs threads internally
        print("FIX initiator started")

    def stop(self):
        self.initiator.stop()
        print("FIX initiator stopped")

    def wait_for_logon(self, timeout=30):
        # Wait until application has a sessionID assigned in onLogon
        start = time.time()
        while not hasattr(self.application, 'sessionID') or self.application.sessionID is None:
            if time.time() - start > timeout:
                raise TimeoutError("Timeout waiting for FIX logon")
            time.sleep(0.1)
        return self.application.sessionID

    def send_order(self, order):
        # Ensure logged on
        self.wait_for_logon()
        # delegate to application which implements send_order method using QuickFIX typed fields
        self.application.send_order(order)

    def _on_exec_report(self, report: dict):
        # publish to RabbitMQ for other services (FastAPI websockets etc.)
        self._rabbit_ch.basic_publish(
            exchange='',
            routing_key='execution_reports',
            body=json.dumps(report),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("Published exec report to RabbitMQ:", report)
