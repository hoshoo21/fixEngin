import quickfix
from .application import Application
import os
import pika, json



class FIXInitiator:

    def __init__(self, config_file):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # initiator folder

        CONFIG_FILE = os.path.join(BASE_DIR, 'client.cfg')

        self.rabbit_connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        self.rabbit_channel = self.rabbit_connection.channel()
        self.rabbit_channel.queue_declare(queue="execution_reports", durable=True)

        self.settings = quickfix.SessionSettings(CONFIG_FILE)
        #self.application = Application(on_exec_report_call_back=self.handle_execution_report)
        self.application = Application()
        self.storefactory = quickfix.FileStoreFactory(self.settings)
        self.logfactory = quickfix.FileLogFactory(self.settings)
        self.initiator = quickfix.SocketInitiator(
            self.application, self.storefactory, self.settings, self.logfactory
        )

    def start(self):
        self.initiator.start()
        print("FIX Initiator started...")

    def stop(self):
        self.initiator.stop()
        print("FIX Initiator stopped...")


    def send_order(self, order_data):
        """
        Send order through FIX via your Application class.
        You need to implement the method in your Application to handle this.
        """
        self.application.send_order(order_data)
        
        
    def handle_execution_report(self, report):
        print("Execution Report received inside app:", report)
        self.rabbit_channel.basic_publish(
                exchange='',
                routing_key='execution_reports',
                body=json.dumps(report),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        print("Execution report forwarded to RabbitMQ")