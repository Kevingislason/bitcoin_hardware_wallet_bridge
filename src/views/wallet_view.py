from bitcointx.core import satoshi_to_coins
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.serial_connection_state import SerialConnectionState
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import (
    Config, BalanceUnits, ChainParameters, NetworkClient
)


class WalletView(QWidget):
    # todo: get rid of
    VIEW_INDEX = 1

    layout: QGridLayout
    current_balance_label: QLabel
    send_button: QPushButton

    watch_only_wallet: WatchOnlyWallet
    serial_connection_state: SerialConnectionState
    controller: MainController

    def __init__(self,
                 watch_only_wallet: WatchOnlyWallet,
                 serial_connection_state: SerialConnectionState,
                 controller: MainController):

        super().__init__()
        self.watch_only_wallet = watch_only_wallet
        self.serial_connection_state = serial_connection_state
        self.controller = controller

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Init current balance label
        self.current_balance_label = QLabel()
        self.current_balance_label.setText("Loading balance...")
        self.layout.addWidget(self.current_balance_label, 0, 0, Qt.AlignCenter)

        self.send_button = QPushButton("Send")
        self.layout.addWidget(self.send_button, 1, 0, Qt.AlignCenter)

        # Connect views to controller
        self.send_button.clicked.connect(self.controller.send_transaction)
        # self._ui.spinBox_amount.valueChanged.connect(self._main_controller.change_amount)
        # self._ui.pushButton_reset.clicked.connect(lambda: self._main_controller.change_amount(0))

        # Listen for model event signals
        # self.watch_only_wallet.unspendable_balance_satoshis_changed.connect(
        #     self.on_unspendable_balance_changed)
        self.watch_only_wallet.spendable_balance_satoshis_changed.connect(
            self.on_spendable_balance_changed)

    # todo: connect balances label to watch only wallet status

    @pyqtSlot(int)
    def on_spendable_balance_changed(self, balance: int):
        CURRENT_BALANCE_TEMPLATE = "Current balance: {balance} {units}"

        if Config.get_balance_units() == BalanceUnits.BTC:
            balance_text = str(satoshi_to_coins(balance))
            units = "BTC"

        elif Config.get_balance_units() == BalanceUnits.SATOSHIS:
            balance_text = str(balance)
            units = "satoshis"

        current_balance_text = CURRENT_BALANCE_TEMPLATE.format(
            balance=balance_text,
            units=units
        )

        self.current_balance_label.setText(current_balance_text)
