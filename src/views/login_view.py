from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import bcrypt
from functools import partial
from utils.password_utils import password_is_correct
from views.wallet_view import WalletView


class LoginView(QWidget):
    VIEW_INDEX = 1

    def __init__(self, change_view):
        super().__init__()
        self.change_view = change_view
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        login_label = QLabel()

        password_form = QLineEdit()
        password_form.setEchoMode(QLineEdit.Password)

        LOGIN_BUTTON_WIDTH = 115
        LOGIN_BUTTON_TEXT = 'Log in'
        login_button = QPushButton()
        login_button.setFixedWidth(LOGIN_BUTTON_WIDTH)
        login_button.setText(LOGIN_BUTTON_TEXT)

        login_button.clicked.connect(
            partial(self.handle_click_login_button, password_form, login_label)
        )

        self.layout.addWidget(login_label, 0, 0, Qt.AlignCenter)
        self.layout.addWidget(password_form, 1, 0, Qt.AlignCenter)
        self.layout.addWidget(login_button, 2, 0, Qt.AlignCenter)

    def handle_click_login_button(self, password_form, login_label):
        if password_is_correct(password_form.text()):
            self.change_view(WalletView.VIEW_INDEX)
        else:
            login_label.setText('Login Failed')
