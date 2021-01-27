from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet

class MainView(QMainWindow):
    main_controller: MainController

    watch_only_wallet: WatchOnlyWallet

    initialize_wallet_view: InitializeWalletView
    wallet_view: WalletView
    status_bar_view: StatusBarView


    def __init__(self, main_controller, watch_only_wallet):
        super().__init__()
        self.initialize_wallet_view = InitializeWalletView(self.main_controller, self.change_view)
        self.wallet_view = WalletView(self.main_controller, self.watch_only_wallet)
        self.status_bar_view = StatusBarView(self.main_controller, self.watch_only_wallet)

        self.central_widget.addWidget(self.initialize_wallet_view)
        self.central_widget.addWidget(self.wallet_view)
        self.setStatusBar(self.status_bar_view)


