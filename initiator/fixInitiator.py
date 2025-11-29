import quickfix
from .application import Application
import os




class FIXInitiator:
    def __init__(self, config_file):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # initiator folder

        CONFIG_FILE = os.path.join(BASE_DIR, 'client.cfg')

        self.settings = quickfix.SessionSettings(CONFIG_FILE)
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
