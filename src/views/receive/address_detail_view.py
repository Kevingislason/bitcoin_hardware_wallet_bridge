from io import BytesIO

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qrcode


from models.watch_only_wallet import WatchOnlyWallet


class AddressDetailView(QFrame):
    def __init__(self, watch_only_wallet: WatchOnlyWallet):
      super().__init__()
      self.watch_only_wallet = watch_only_wallet


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
      # self.address_name_container.layout.setContentsMargins(0, 0, 0, 0)
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
      address = self.watch_only_wallet.ui_addresses[address_idx]

      # Set freshness label
      icon_style = QStyle.SP_DialogYesButton if address.is_fresh else QStyle.SP_DialogNoButton
      icon_tooltip_text = "This address is fresh" if address.is_fresh else "This address has aleady been used"
      icon = self.style().standardIcon(icon_style)
      pixmap = icon.pixmap(QSize(20, 20))
      self.address_freshness_icon.setPixmap(pixmap)
      self.address_freshness_icon.setToolTip(icon_tooltip_text)

      # Set QR Code
      buffer = BytesIO()
      image = qrcode.make(str(address))
      image.save(buffer, "PNG")
      qr_code_pixmap = QPixmap()
      qr_code_pixmap.loadFromData(buffer.getvalue(), "PNG")
      qr_code_pixmap = qr_code_pixmap.scaledToHeight(300)
      self.qr_code.setPixmap(qr_code_pixmap)

      # Set address text to new address
      self.address_name_text.setText(address.label) #
      self.address_name_text.setText(address.label)
      self.address_text.setText("Receiving Address: {}".format(str(address)))

      # Set key path
      self.key_path_text.setText(f"Key Path: {address.key_path}")





