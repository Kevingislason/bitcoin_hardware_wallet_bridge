from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import bcrypt
from functools import partial


class WalletView(QWidget):
    VIEW_INDEX = 2

    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        unspent_balance_label = QLabel()
        unspent_balance_label.setText('Current balance: 6.15 BTC')

        self.layout.addWidget(unspent_balance_label, 0, 0, Qt.AlignCenter)
