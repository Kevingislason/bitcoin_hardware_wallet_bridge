from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class ErrorMessage:
    NO_ADDRESS = "Must specify recipient's address"
    INVALID_ADDRESS = "Specified address is invalid"
    INSUFFICIENT_FUNDS = "Insufficient funds"
    INSUFFICIENT_FUNDS_AFTER_FEES = "Insufficient funds after fees"
    INVALID_SPEND = "Amount is invalid"

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
        self.layout.addWidget(self.okay_button)
        self.okay_button.clicked.connect(self.handle_click_okay_button)


    def handle_click_okay_button(self):
      self.close()


    def show(self, error_message: ErrorMessage):
        self.error_message.setText(error_message)
        self.exec_()
        self.activateWindow()
        # self.setFocus()
