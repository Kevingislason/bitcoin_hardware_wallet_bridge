from io import BytesIO

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import qrcode
from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from models.wallet_address import WalletAddress


class AddressDetailView(QFrame):
    controller: MainController
    watch_only_wallet: WatchOnlyWallet
    address: WalletAddress

    def __init__(self, controller: MainController, watch_only_wallet: WatchOnlyWallet):
        super().__init__()
        self.controller = controller
        self.watch_only_wallet = watch_only_wallet
        self.watch_only_wallet.spendable_balance_satoshis_changed.connect(
            self.handle_balance_changed
        )
        self.watch_only_wallet.incoming_balance_satoshis_changed.connect(
            self.handle_balance_changed
        )
        self.address = None

        self.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.size_policy.setHorizontalStretch(3)
        self.setSizePolicy(self.size_policy)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.stack = QStackedWidget()
        self.no_address_text = QLabel("Generate a receiving address to continue")
        self.no_address_text.setAlignment(Qt.AlignCenter)

        self.details = QWidget()
        self.details.layout = QVBoxLayout()
        self.details.layout.setSpacing(30)
        self.details.layout.setAlignment(Qt.AlignCenter)
        self.details.setLayout(self.details.layout)

        self.address_name_container = QWidget()
        self.address_name_container.layout = QHBoxLayout()
        self.address_name_container.layout.setAlignment(Qt.AlignCenter)
        self.address_name_container.setLayout(self.address_name_container.layout)

        self.address_freshness_icon = QLabel()
        self.address_freshness_icon.setAlignment(Qt.AlignCenter)

        self.address_name_text = QLabel()
        self.address_name_text.setAlignment(Qt.AlignCenter)
        self.address_name_text.font = QFont()
        self.address_name_text.font.setPointSizeF(18)
        self.address_name_text.font.setBold(True)
        self.address_name_text.setFont(self.address_name_text.font)
        self.address_name_container.layout.addWidget(self.address_freshness_icon)
        self.address_name_container.layout.addWidget(self.address_name_text)

        self.qr_code = QLabel()
        self.qr_code.setAlignment(Qt.AlignCenter)

        self.address_text = QLabel()
        self.address_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.key_path_text = QLabel()
        self.key_path_text.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.lower_details_container = QWidget()
        self.lower_details_container.layout = QVBoxLayout()
        self.lower_details_container.setLayout(self.lower_details_container.layout)
        self.lower_details_container.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.lower_details_container.layout.addWidget(self.address_text)
        self.lower_details_container.layout.addWidget(self.key_path_text)

        self.details.layout.addWidget(self.address_name_container)
        self.details.layout.addWidget(self.qr_code)
        self.details.layout.addWidget(self.lower_details_container)

        self.stack.addWidget(self.no_address_text)
        self.stack.addWidget(self.details)

        self.layout.addWidget(self.stack)

    def handle_address_changed(self, address_list):
        self.stack.setCurrentIndex(1)
        address_idx = address_list.currentRow()
        self.address = self.watch_only_wallet.ui_addresses[address_idx]
        self.set_address_icon()
        self.set_qr_code()
        self.address_name_text.setText(self.address.label)
        self.address_text.setText("Receiving Address: {}".format(str(self.address)))
        self.key_path_text.setText(f"Key Path: {self.address.key_path}")
        self.controller.request_hardware_wallet_display_address(self.address.key_path)

    def set_address_icon(self):
        icon_style = (
          QStyle.SP_DialogYesButton if self.address.is_fresh
          else QStyle.SP_DialogNoButton
        )
        icon_tooltip_text = (
          "This address is fresh" if self.address.is_fresh
          else "This address has aleady been used"
        )
        icon = self.style().standardIcon(icon_style)
        pixmap = icon.pixmap(QSize(20, 20))
        self.address_freshness_icon.setPixmap(pixmap)
        self.address_freshness_icon.setToolTip(icon_tooltip_text)

    def set_qr_code(self):
        buffer = BytesIO()
        image = qrcode.make(str(self.address))
        image.save(buffer, "PNG")
        qr_code_pixmap = QPixmap()
        qr_code_pixmap.loadFromData(buffer.getvalue(), "PNG")
        qr_code_pixmap = qr_code_pixmap.scaledToHeight(300)
        self.qr_code.setPixmap(qr_code_pixmap)


    @pyqtSlot(int)
    def handle_balance_changed(self, _: int):
        if self.address:
            self.set_address_icon()



