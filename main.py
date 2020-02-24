import sys
from PyQt5.QtWidgets import QWidget, QApplication


class App(QWidget):
    title = 'Bitcoin Wallet'
    CONST_DEFAULT_LEFT = 10
    CONST_DEFAULT_TOP = 10
    CONST_DEFAULT_WIDTH = 1315
    CONST_DEFAULT_HEIGHT = 950

    def __init__(self):
        super().__init__()
        self.init_ui()
        if self.is_first_login():
            self.handle_first_login()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.CONST_DEFAULT_LEFT, self.CONST_DEFAULT_TOP,
                         self.CONST_DEFAULT_WIDTH, self.CONST_DEFAULT_HEIGHT)
        self.show()

    def is_first_login(self):
        # todo

    def handle_first_login(self):
        # todo


def main():

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
