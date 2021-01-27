from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from networking.serial.serial_client import SerialClient
from persistence.wallet_file import WalletFile


class InitializeWalletView(QWidget):
    # todo: shouldn't hard code these
    VIEW_INDEX = 0

    layout: QVBoxLayout
    connect_hardware_wallet_instruction_label: QLabel

    def __init__(self, controller: MainController, change_view):
        super().__init__()
        self.controller = controller
        self.change_view = change_view
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        connect_hardware_wallet_instruction_label = QLabel(
            "Connect your hardware wallet to continue")
        self.layout.addWidget(connect_hardware_wallet_instruction_label)


        # self.controller.await_hardware_wallet_connection()
