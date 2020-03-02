from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import bcrypt
from functools import partial


class Login_View(QGridLayout):
    def __init__(self, set_layout):
        super().__init__()
        self.set_layout = set_layout

        login_label = QLabel()

        password_form = QLineEdit()
        password_form.setEchoMode(QLineEdit.Password)

        LOGIN_BUTTON_WIDTH = 115
        login_button = QPushButton()
        login_button.setFixedWidth(LOGIN_BUTTON_WIDTH)
        login_button.setText('Log in')

        login_button.clicked.connect(
            partial(self.handle_click_login_button, password_form, login_label)
        )

        self.addWidget(login_label, 0, 0, Qt.AlignCenter)
        self.addWidget(password_form, 1, 0, Qt.AlignCenter)
        self.addWidget(login_button, 2, 0, Qt.AlignCenter)

    def handle_click_login_button(self, password_form, login_label):
        if self.password_is_correct(password_form.text()):
            print('login successful')
        else:
            print('login failed')

    def password_is_correct(self, password_attempt):
        password_attempt = password_attempt.encode('utf-8')
        saved_password_file = open('password.bfe', 'r')
        if saved_password_file.mode == 'r':
            saved_password = saved_password_file.read().encode('utf-8')
            return bcrypt.checkpw(password_attempt, saved_password)
        else:
            return False
