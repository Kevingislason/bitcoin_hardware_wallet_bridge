from typing import Optional

from bitcointx.core import satoshi_to_coins
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from views.receive.receive_view import ReceiveView
from views.send.send_view import SendView


class WalletView(QWidget):
    controller: MainController
    watch_only_wallet: WatchOnlyWallet

    send_tab: SendView
    receive_tab: ReceiveView

    def __init__(self, main_controller: MainController, watch_only_wallet: WatchOnlyWallet):
        super().__init__()
        self.controller = main_controller
        self.watch_only_wallet = watch_only_wallet

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.send_tab = SendView(main_controller, watch_only_wallet)
        self.receive_tab = ReceiveView(main_controller, watch_only_wallet)
        self.tabs.addTab(self.send_tab, "Send")
        self.tabs.addTab(self.receive_tab, "Receive")
        self.layout.addWidget(self.tabs)
