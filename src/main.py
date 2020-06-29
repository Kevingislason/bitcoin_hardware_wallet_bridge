from os import path
import sys
import configparser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from views.awaiting_serial_connection_view import AwaitingSerialConnectionView
from views.wallet_view import WalletView


class App(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init_ui()

        if not self.wallet_is_connected():
            self.change_view(AwaitingSerialConnectionView.VIEW_INDEX)
        else:
            self.change_view(WalletView.VIEW_INDEX)

    def init_ui(self):
        # Set window title
        CONST_WINDOW_TITLE = "Bitcoin Wallet"
        self.setWindowTitle(CONST_WINDOW_TITLE)
        # Set window size
        CONST_DEFAULT_LEFT = 10
        CONST_DEFAULT_TOP = 10
        CONST_DEFAULT_WIDTH = 750
        CONST_DEFAULT_HEIGHT = 500
        self.setGeometry(CONST_DEFAULT_LEFT, CONST_DEFAULT_TOP,
                         CONST_DEFAULT_WIDTH, CONST_DEFAULT_HEIGHT)
        # Init application "pages"
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(
            AwaitingSerialConnectionView(self.change_view))
        self.central_widget.addWidget(WalletView(self.change_view))
        # todo: add settings page
        self.show()

    # todo: implement
    def wallet_is_connected(self):
        return False

    def is_first_login(self):
        return not path.exists("config.ini")

    def init_config_file(self):
        config = configparser.ConfigParser()
        # todo: what default configs do I actually need?
        with open('config.ini', 'w+') as configfile:
            config.write(configfile)

        configfile.close()


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    # from network.block_explorer_client import BlockExplorerClient
    # BlockExplorerClient().get_utxos(["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"])
