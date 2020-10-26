from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController

from models.watch_only_wallet import WatchOnlyWallet
from models.serial_connection_state import SerialConnectionState

class SendView(QWidget):
    def __init__(self, watch_only_wallet: WatchOnlyWallet,
              serial_connection_state: SerialConnectionState):

        super().__init__()
        self.watch_only_wallet = watch_only_wallet
        self.serial_connection_state = serial_connection_state
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
