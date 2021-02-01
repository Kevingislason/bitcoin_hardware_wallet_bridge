import configparser
import sys
from os import path

from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import Config
from views.main_view import MainView


class AbacusWalletBridge():
    main_controller: MainController
    watch_only_wallet: WatchOnlyWallet
    main_view: MainView


    def __init__(self):
        super().__init__()
        if not Config.exists():
            Config.set_defaults()
        self.watch_only_wallet = WatchOnlyWallet()
        self.main_controller = MainController(self.watch_only_wallet)
        self.main_view = MainView(self.main_controller, self.watch_only_wallet)
        self.main_controller.sync_to_blockchain_loop_async()
        self.main_controller.sync_to_hardware_wallet_loop_async()

def main():
    app = QApplication(sys.argv)
    font = QFont("Courier", 15)
    app.setFont(font)
    ex = AbacusWalletBridge()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
