from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class AwaitingSerialConnectionView(QWidget):
    VIEW_INDEX = 0

    def __init__(self, change_view):
        super().__init__()
        self.change_view = change_view

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        connect_hardware_wallet_instruction_label = QLabel(
            'Connect your hardware wallet to continue')

        self.layout.addWidget(connect_hardware_wallet_instruction_label)
