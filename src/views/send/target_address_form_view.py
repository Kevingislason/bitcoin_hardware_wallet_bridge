
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TargetAddressForm(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.target_address_label = QLabel("Pay to:")
        self.target_address_label.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.target_address_label.size_policy.setHorizontalStretch(1)
        self.target_address_label.setSizePolicy(self.target_address_label.size_policy)
        self.target_address_input = QLineEdit()

        self.target_address_input.setMaxLength(74) # max address length
        self.target_address_input.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.target_address_input.size_policy.setHorizontalStretch(8)
        self.target_address_input.setSizePolicy(self.target_address_input.size_policy)

        self.target_address_spacer = QLabel("")
        self.target_address_spacer.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.target_address_spacer.size_policy.setHorizontalStretch(1)
        self.target_address_spacer.setSizePolicy(self.target_address_spacer.size_policy)


        self.layout.addWidget(self.target_address_label)
        self.layout.addWidget(self.target_address_input)
        self.layout.addWidget(self.target_address_spacer)
