from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from persistence.wallet_file import WalletFile
from views.initialize_wallet_view import InitializeWalletView
from views.status_bar_view import StatusBarView
from views.wallet_view import WalletView


class MainView(QMainWindow):
    main_controller: MainController
    watch_only_wallet: WatchOnlyWallet

    initialize_wallet_view: InitializeWalletView
    wallet_view: WalletView
    status_bar_view: StatusBarView

    WINDOW_TITLE = "Abacus Wallet"
    INIT_WALLET_PAGE_INDEX = 0
    WALLET_PAGE_INDEX = 1
    DEFAULT_LEFT = 0
    DEFAULT_TOP = 0
    DEFAULT_WIDTH = 950
    DEFAULT_HEIGHT = 600


    def __init__(self, main_controller, watch_only_wallet):
        super().__init__()
        self.main_controller = main_controller
        self.watch_only_wallet = watch_only_wallet
        self.init_base_ui()
        self.init_app_views()
        self.show()

        self.main_controller.watch_only_wallet_initialized.connect(
          self.handle_watch_only_wallet_initialized
        )

        if WalletFile.exists():
            self.init_status_bar()
            self.central_widget.setCurrentIndex(self.WALLET_PAGE_INDEX)
        else:
            self.central_widget.setCurrentIndex(self.INIT_WALLET_PAGE_INDEX)


    def init_base_ui(self):
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(
          self.DEFAULT_LEFT, self.DEFAULT_TOP,
          self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT
        )
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)


    def init_app_views(self):
        self.init_initialize_wallet_view()
        self.init_wallet_view()


    def init_wallet_view(self):
        self.wallet_view = WalletView(self.main_controller, self.watch_only_wallet)
        self.central_widget.addWidget(self.wallet_view)


    def init_initialize_wallet_view(self):
        self.initialize_wallet_view = InitializeWalletView(self.main_controller)
        self.central_widget.addWidget(self.initialize_wallet_view)


    def init_status_bar(self):
        self.status_bar_view = StatusBarView(self.main_controller, self.watch_only_wallet)
        self.setStatusBar(self.status_bar_view)

    @pyqtSlot()
    def handle_watch_only_wallet_initialized(self):
        self.central_widget.setCurrentIndex(self.WALLET_PAGE_INDEX)
        self.init_status_bar()
