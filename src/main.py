import configparser
import sys
from os import path

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from networking.blockchain.block_explorer_client import BlockExplorerClient
from networking.serial.serial_client import SerialClient
from persistence.config import (
    Config, BlockchainClient, BalanceUnits, ChainParameters
)
from persistence.init_wallet_file import InitWalletFile
from views.initialize_wallet_view import InitializeWalletView
from views.status_bar_view import StatusBarView
from views.wallet_view import WalletView


class BitcoinHardwareWalletBridge(QMainWindow):
    main_controller: MainController

    watch_only_wallet: WatchOnlyWallet

    initialize_wallet_view: InitializeWalletView
    wallet_view: WalletView
    status_bar_view :StatusBarView

    def __init__(self):
        super().__init__()
        if not Config.exists():
            Config.set_defaults()

        self.init_ui()

        self.watch_only_wallet = WatchOnlyWallet()
        self.main_controller = MainController(self.watch_only_wallet)

        self.initialize_wallet_view = InitializeWalletView(self.main_controller, self.change_view)
        self.wallet_view = WalletView(self.main_controller, self.watch_only_wallet)
        self.status_bar_view = StatusBarView(self.main_controller, self.watch_only_wallet)

        self.central_widget.addWidget(self.initialize_wallet_view)
        self.central_widget.addWidget(self.wallet_view)
        self.setStatusBar(self.status_bar_view)

        if InitWalletFile.exists():
            self.change_view(WalletView.VIEW_INDEX)

        self.main_controller.sync_to_blockchain_loop_async()
        self.main_controller.sync_to_hardware_wallet_loop_async()

    def init_ui(self):
        # Set window title
        WINDOW_TITLE = "Bitcoin Wallet"
        self.setWindowTitle(WINDOW_TITLE)
        # Set window size
        DEFAULT_LEFT = 0
        DEFAULT_TOP = 0
        DEFAULT_WIDTH = 950
        DEFAULT_HEIGHT = 600
        self.setGeometry(DEFAULT_LEFT, DEFAULT_TOP,
                         DEFAULT_WIDTH, DEFAULT_HEIGHT)
        # Create app "pages"
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.show()

    def change_view(self, new_view_index: int):
        self.central_widget.setCurrentIndex(new_view_index)


def main():
    app = QApplication(sys.argv)
    font = QFont("Courier", 15)
    app.setFont(font)
    ex = BitcoinHardwareWalletBridge()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
