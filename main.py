from os import path
import sys
import configparser
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


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

    def show_first_login_view(self):
        self.layout = QGridLayout()
        SET_PASSWORD_BUTTON_WIDTH = 115
        set_password_button = QPushButton()
        set_password_button.setFixedWidth(SET_PASSWORD_BUTTON_WIDTH)
        set_password_button.setText('Save password')
        passwordForm = QLineEdit()
        passwordForm.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(passwordForm, 0, 0, Qt.AlignCenter)
        self.layout.addWidget(set_password_button, 1, 0, Qt.AlignCenter)
        self.setLayout(self.layout)

    # def validate_password(self):
    #


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
