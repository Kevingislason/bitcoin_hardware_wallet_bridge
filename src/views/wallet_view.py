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
from models.serial_connection_state import SerialConnectionState
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import (
    Config, BalanceUnits, ChainParameters, BlockchainClient
)
from views.send_view import SendView
from views.receive_view import ReceiveView

class WalletView(QWidget):
    # todo: get rid of
    VIEW_INDEX = 1

    # Controller
    controller: MainController

    # Models
    watch_only_wallet: WatchOnlyWallet
    serial_connection_state: SerialConnectionState

    # Tabs
    send_tab: SendView
    receive_tab: ReceiveView

    # Widgetss
    layout: QGridLayout
    tabs: QTabWidget
    current_balance_label: QLabel
    send_button: QPushButton



    def __init__(self,
                 main_controller: MainController,
                 watch_only_wallet: WatchOnlyWallet,
                 serial_connection_state: SerialConnectionState

                 ):

        super().__init__()
        self.controller = main_controller
        self.watch_only_wallet = watch_only_wallet
        self.serial_connection_state = serial_connection_state

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.send_tab = SendView(watch_only_wallet, serial_connection_state)
        self.receive_tab = ReceiveView(main_controller, watch_only_wallet)
        # self.tabs.resize(1000,1000)
        self.tabs.addTab(self.send_tab, "Send")
        self.tabs.addTab(self.receive_tab, "Receive")







        # Init current balance label
        # self.balance_display = QStackedWidget()

        # self.balance_loader = QtWaitingSpinner()
        # self.balance_display.add_widget(self.balance_label)

        # self.display_spendable_balance(self.watch_only_wallet.spendable_balance_satoshis)
        # self.layout.addWidget(self.balance_label, 0, 0, Qt.AlignCenter)

        # self.send_tab.layout.addWidget(self.balance_label)

        self.layout.addWidget(self.tabs)
