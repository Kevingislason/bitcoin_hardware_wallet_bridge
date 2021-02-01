from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from networking.serial.serial_client import SerialClient
from persistence.hardware_wallet_file import HardwareWalletFile
from persistence.wallet_file import WalletFile


class InitializeWalletView(QWidget):
    CONNECT_HARDWARE_WALLET_TEXT = "Connect your hardware wallet to begin"
    INIT_HARDWARE_WALLET_TEXT = "Follow the prompts on your hardware wallet's screen"
    LOADING_TEXT = "Loading wallet..."

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.init_event_handlers()


    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.init_wallet_label = QLabel()
        self.init_wallet_label.setAlignment(Qt.AlignCenter)
        if HardwareWalletFile.exists():
            self.init_wallet_label.setText(self.LOADING_TEXT)
        else:
            self.init_wallet_label.setText(self.CONNECT_HARDWARE_WALLET_TEXT)
        self.layout.addWidget(self.init_wallet_label)


    def init_event_handlers(self):
        self.controller.serial_client.connection.connect(
            self.handle_serial_connection_change
        )
        self.controller.hardware_wallet_initialized.connect(
            self.handle_hardware_wallet_initialized
        )
        self.controller.hardware_wallet_initialized.connect(
            self.handle_hardware_wallet_loaded
        )


    @pyqtSlot(bool)
    def handle_serial_connection_change(self, is_connected):
        if is_connected:
            self.handle_serial_connected()
        else:
            self.handle_serial_disconnected()


    def handle_serial_connected(self):
        if not HardwareWalletFile.exists():
            self.init_wallet_label.setText(self.INIT_HARDWARE_WALLET_TEXT)


    def handle_serial_disconnected(self):
        if not HardwareWalletFile.exists():
            self.init_wallet_label.setText(self.CONNECT_HARDWARE_WALLET_TEXT)


    @pyqtSlot()
    def handle_hardware_wallet_initialized(self):
        self.init_wallet_label.setText(self.LOADING_TEXT)


    @pyqtSlot()
    def handle_hardware_wallet_loaded(self):
        self.init_wallet_label.setText(self.LOADING_TEXT)
