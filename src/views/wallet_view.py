from typing import Optional

from bitcointx.core import satoshi_to_coins
from bitcointx.wallet import (
    T_CCoinAddress as AddressType,
    T_P2PKHCoinAddress as P2PKHAddressType,
    T_P2SHCoinAddress as P2SHAddressType,
    T_P2WPKHCoinAddress as P2WPKHAddressType
)

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import (
    Config, BalanceUnits, ChainParameters, BlockchainClient
)
from views.send.send_view import SendView
from views.receive.receive_view import ReceiveView

class WalletView(QWidget):
    # todo: get rid of
    VIEW_INDEX = 1

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
