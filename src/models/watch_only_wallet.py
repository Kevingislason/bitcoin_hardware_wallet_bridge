from typing import List

from PyQt5.QtCore import QObject, pyqtSignal

from models.tx_in import TxIn


class WatchOnlyWallet(QObject):
    tx_ins: List[TxIn]

    unspendable_balance_satoshis_changed = pyqtSignal(int)
    spendable_balance_satoshis_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._spendable_balance_satoshis = None
        self._unspendable_balance_satoshis = None

    @property
    def unspendable_balance_satoshis(self) -> int:
        return self._unspendable_balance_satoshis

    @unspendable_balance_satoshis.setter
    def unspendable_balance_satoshis(self, new_balance: int):
        self._unspendable_balance_satoshis = new_balance
        self.unspendable_balance_satoshis_changed.emit(new_balance)

    @property
    def spendable_balance_satoshis(self) -> int:
        return self._spendable_balance_satoshis

    @spendable_balance_satoshis.setter
    def spendable_balance_satoshis(self, new_balance: int):
        self._spendable_balance_satoshis = new_balance
        self.spendable_balance_satoshis_changed.emit(new_balance)
