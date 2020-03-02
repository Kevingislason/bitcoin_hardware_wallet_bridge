from os import path
import sys
import configparser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from create_password_view import Create_Password_View
from login_view import Login_View


class App(QWidget):
    title = 'Bitcoin Wallet'
    CONST_DEFAULT_LEFT = 10
    CONST_DEFAULT_TOP = 10
    CONST_DEFAULT_WIDTH = 750
    CONST_DEFAULT_HEIGHT = 500

    def __init__(self):
        super().__init__()
        self.init_ui()
        if self.is_first_login():
            self.show_first_login_view()
            self.init_config_file()
        else:
            self.show_login_view()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.CONST_DEFAULT_LEFT, self.CONST_DEFAULT_TOP,
                         self.CONST_DEFAULT_WIDTH, self.CONST_DEFAULT_HEIGHT)
        self.show()

    def is_first_login(self):
        return not path.exists("password.bfe")

    def init_config_file(self):
        config = configparser.ConfigParser()
        # todo: what default configs do I actually need?
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)

        configfile.close()

    def show_first_login_view(self):
        self.setLayout(Create_Password_View(self.set_layout))

    def show_login_view(self):
        self.setLayout(Login_View(self.set_layout))

    def set_layout(self, new_layout):
        self.setLayout(new_layout)


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
