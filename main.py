from os import path
from functools import partial
import sys
import configparser
import bcrypt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class App(QWidget):
    title = 'Bitcoin Wallet'
    CONST_DEFAULT_LEFT = 10
    CONST_DEFAULT_TOP = 10
    CONST_DEFAULT_WIDTH = 750
    CONST_DEFAULT_HEIGHT = 500
    layout = None

    def __init__(self):
        super().__init__()
        self.init_ui()
        if not self.is_first_login():
            self.show_first_login_view()
            self.init_config_file()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.CONST_DEFAULT_LEFT, self.CONST_DEFAULT_TOP,
                         self.CONST_DEFAULT_WIDTH, self.CONST_DEFAULT_HEIGHT)
        self.show()

    def is_first_login(self):
        # todo: temporarily wrong for dev purposes
        return not path.exists("config.ini")

    def init_config_file(self):
        config = configparser.ConfigParser()
        # todo: what default configs do I actually need?
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)

        configfile.close()

    # todo: move this into its own class extending layout
    def show_first_login_view(self):
        self.layout = QGridLayout()
        create_password_instruction_label = QLabel()
        CREATE_PASSWORD_INSTRUCTION_LABEL_TEXT = 'Choose a password with:\n• at least eight characters\n• at least one capital letter\n• at least one number'
        create_password_instruction_label.setText(
            CREATE_PASSWORD_INSTRUCTION_LABEL_TEXT)

        create_password_form = QLineEdit()
        create_password_form.setEchoMode(QLineEdit.Password)
        CREATE_PASSWORD_BUTTON_WIDTH = 115
        create_password_button = QPushButton()
        create_password_button.setFixedWidth(CREATE_PASSWORD_BUTTON_WIDTH)
        create_password_button.setText('Save password')
        create_password_button.clicked.connect(
            partial(self.handle_click_create_password_button, create_password_form, create_password_instruction_label))

        self.layout.addWidget(
            create_password_instruction_label, 0, 0, Qt.AlignCenter)
        self.layout.addWidget(create_password_form, 1, 0, Qt.AlignCenter)
        self.layout.addWidget(create_password_button, 2, 0, Qt.AlignCenter)
        self.setLayout(self.layout)

    def handle_click_create_password_button(self, password_form, create_password_instruction_label):
        password_validation_errors = self.validate_password(
            password_form.text())
        if len(password_validation_errors):
            create_password_instruction_label_text = "•" + '\n•'.join(
                password_validation_errors)
            create_password_instruction_label.setText(
                create_password_instruction_label_text)
        else:
            self.save_password(password_form.text())

    def validate_password(self, password):
        validation_errors = []
        if len(password) < 8:
            validation_errors.append(
                "password must have at least eight characters")
        if not any(c.isupper() for c in password):
            validation_errors.append(
                "password must have at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            validation_errors.append(
                "password must have at least one number")
        return validation_errors

    def save_password(self, password):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)
        with open('secrets.bfe', 'w+') as secrets:
            secrets.write(hashed_password.decode('utf-8'))
        secrets.close()


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
