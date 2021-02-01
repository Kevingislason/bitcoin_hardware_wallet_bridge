from bitcointx.core import satoshi_to_coins
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import BalanceUnits, Config, Network
from utils.unit_utils import get_currency_symbol


class StatusBarView(QStatusBar):

    SPENDABLE_BALANCE_TEMPLATE = "Balance: {balance} {currency_symbol}"
    INCOMING_BALANCE_TEMPLATE = " (+ {balance} {currency_symbol} incoming)"

    watch_only_wallet: WatchOnlyWallet
    controller: MainController
    spendable_balance: int
    incoming_balance: int

    def __init__(self, controller: MainController, watch_only_wallet: WatchOnlyWallet):

        super().__init__()
        self.watch_only_wallet = watch_only_wallet
        self.controller = controller

        self.balance_label_container = QWidget()
        self.balance_label_container.layout = QHBoxLayout()
        self.balance_label_container.setLayout(self.balance_label_container.layout)
        self.balance_label = QLabel()
        self.balance_label.setAlignment(Qt.AlignCenter)

        self.connection_label_container = QWidget()
        self.connection_label_container.layout = QHBoxLayout()
        self.connection_label_container.setLayout(self.connection_label_container.layout)
        self.connection_label = QLabel("Connected")
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.addWidget(self.balance_label, 0)
        self.addPermanentWidget(self.connection_label, 0)

        self.watch_only_wallet.spendable_balance_satoshis_changed.connect(
            self.on_spendable_balance_changed
        )
        self.watch_only_wallet.incoming_balance_satoshis_changed.connect(
            self.on_incoming_balance_changed
        )
        self.controller.blockchain_client.connection.connect(
            self.on_network_connection_update
        )
        self.spendable_balance = self.watch_only_wallet.spendable_balance_satoshis
        self.incoming_balance = self.watch_only_wallet.incoming_balance_satoshis
        self.display_balance()

    @pyqtSlot(int)
    def on_spendable_balance_changed(self, balance: int):
        self.spendable_balance = balance
        self.display_balance()

    @pyqtSlot(int)
    def on_incoming_balance_changed(self, balance: int):
        self.incoming_balance = balance
        self.display_balance()

    @pyqtSlot(bool)
    def on_network_connection_update(self, is_connected: bool):
        if is_connected:
            self.connection_label.setText("Connected")
        else:
            self.connection_label.setText("<font color='red'>Disconnected</font>")

    def display_balance(self):
        balance_units = Config.get_balance_units()

        if balance_units == BalanceUnits.BTC:
            spendable_balance_text = str(satoshi_to_coins(self.spendable_balance))
            incoming_balance_text = str(satoshi_to_coins(self.incoming_balance))
        elif balance_units == BalanceUnits.SATOSHIS:
            spendable_balance_text = str(self.spendable_balance)
            incoming_balance_text = str(self.incoming_balance)

        currency_symbol = get_currency_symbol(
            self.controller.network,
            balance_units
        )
        balance_text = self.SPENDABLE_BALANCE_TEMPLATE.format(
            balance=spendable_balance_text,
            currency_symbol=currency_symbol
        )
        if self.incoming_balance > 0:
            incoming_balance_text = self.INCOMING_BALANCE_TEMPLATE.format(
                balance=incoming_balance_text,
                currency_symbol=currency_symbol
            )
            balance_text += incoming_balance_text

        self.balance_label.setText(balance_text)
