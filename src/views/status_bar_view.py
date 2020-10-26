from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from bitcointx.core import satoshi_to_coins

from models.serial_connection_state import SerialConnectionState
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import (
    Config, BalanceUnits, ChainParameters, BlockchainClient
)


class StatusBarView(QStatusBar):

    watch_only_wallet: WatchOnlyWallet
    serial_connection_state: SerialConnectionState

    def __init__(self, watch_only_wallet: WatchOnlyWallet,
                serial_connection_state: SerialConnectionState):

      super().__init__()
      self.watch_only_wallet = watch_only_wallet
      self.serial_connection_state = serial_connection_state

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

      spendable_balance = self.watch_only_wallet.spendable_balance_satoshis
      self.display_spendable_balance(spendable_balance)

    @pyqtSlot(int)
    def on_spendable_balance_changed(self, balance: int):
        self.display_spendable_balance(balance)


    def display_spendable_balance(self, balance: int):
        BALANCE_TEMPLATE = "Balance: {balance} {units}"

        if Config.get_balance_units() == BalanceUnits.BTC:
            balance_text = str(satoshi_to_coins(balance))
            units = "BTC"

        elif Config.get_balance_units() == BalanceUnits.SATOSHIS:
            balance_text = str(balance)
            units = "satoshis"

        current_balance_text = BALANCE_TEMPLATE.format(
            balance=balance_text,
            units=units
        )

        self.balance_label.setText(current_balance_text)



