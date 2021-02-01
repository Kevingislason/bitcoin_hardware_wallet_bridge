from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ErrorMessage:
    NO_ADDRESS = "Must specify recipient's address"
    INVALID_ADDRESS = "Specified address is invalid"
    INSUFFICIENT_FUNDS = "Insufficient funds"
    INSUFFICIENT_FUNDS_AFTER_FEES = "Insufficient funds after fees"
    INVALID_SPEND = "Amount is invalid"
    TX_REJECTED = "Transaction canceled;\n rejected by hardware wallet"
    TX_BROADCAST_FAILED = "Transaction canceled;\n failed to broadcast"
    SERIAL_DISCONNECT = "Transaction canceled;\n hardware wallet disconnected"
    GAP_LIMIT_REACHED = "Gap limit reached;\n use an existing address\n before generating new addresses"


class ErrorModal(QDialog):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setModal(True)

        self.error_message = QLabel("")
        self.layout.addWidget(self.error_message)

        self.okay_button = QPushButton("Okay")
        self.okay_button.setMaximumWidth(100)
        self.okay_button.setAutoDefault(False)
        self.okay_button.setDefault(False)
        self.layout.addWidget(self.okay_button, alignment=Qt.AlignCenter)
        self.okay_button.clicked.connect(self.handle_click_okay_button)



    def handle_click_okay_button(self):
      self.close()


    def show(self, error_message: ErrorMessage):
        self.error_message.setText(error_message)
        self.exec_()
        self.activateWindow()
