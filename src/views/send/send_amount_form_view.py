
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from constants.money_constants import BTC_POINTS_PRECISION, MAX_BTC


class SendAmountForm(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.send_amount_label = QLabel("Amount:")
        self.send_amount_label.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.send_amount_label.size_policy.setHorizontalStretch(1)
        self.send_amount_label.setSizePolicy(self.send_amount_label.size_policy)

        self.send_amount_input = QLineEdit()
        self.send_amount_input.setPlaceholderText("BTC")
        self.send_amount_input.validator = QDoubleValidator(0, MAX_BTC, BTC_POINTS_PRECISION)
        self.send_amount_input.setValidator(self.send_amount_input.validator)
        self.send_amount_input.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.send_amount_input.size_policy.setHorizontalStretch(2)
        self.send_amount_input.setSizePolicy(self.send_amount_input.size_policy)

        self.send_max_amount_button = QPushButton("Max")
        self.send_max_amount_button.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.send_max_amount_button.size_policy.setHorizontalStretch(1)
        self.send_max_amount_button.setSizePolicy(self.send_max_amount_button.size_policy)

        self.send_amount_spacer = QLabel("")
        self.send_amount_spacer.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.send_amount_spacer.size_policy.setHorizontalStretch(6)
        self.send_amount_spacer.setSizePolicy(self.send_amount_spacer.size_policy)

        self.layout.addWidget(self.send_amount_label)
        self.layout.addWidget(self.send_amount_input)
        self.layout.addWidget(self.send_max_amount_button)
        self.layout.addWidget(self.send_amount_spacer)
