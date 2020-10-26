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

        # Address details
      # self.address_detail_frame.setFrameShape(QFrame.StyledPanel)

      self.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
      self.size_policy.setHorizontalStretch(3)
      self.setSizePolicy(self.size_policy)
      self.layout = QVBoxLayout()
      self.setLayout(self.layout)



      self.stack = QStackedWidget()

      self.no_address_text = QLabel("Generate a receiving address to continue")
      self.no_address_text.setAlignment(Qt.AlignCenter)
      self


      self.details = QWidget()
      self.details.layout = QVBoxLayout()
      self.details.setLayout(self.details.layout)
      self.details.layout.setAlignment(Qt.AlignCenter)
      self.address_name_text = QLabel()
      self.address_name_text.setAlignment(Qt.AlignCenter)
      self.qr_code = QLabel()
      self.qr_code.setAlignment(Qt.AlignCenter)
      self.address_text = QLabel()
      self.key_path_text = QLabel()
      self.details.layout.addWidget(self.address_name_text)
      self.details.layout.addWidget(self.qr_code)
      self.details.layout.addWidget(self.address_text)
      self.details.layout.addWidget(self.key_path_text)




      self.stack.addWidget(self.no_address_text)
      self.stack.addWidget(self.details)

      self.layout.addWidget(self.stack)



    def handle_address_changed(self, address_list):
      self.stack.setCurrentIndex(1)
      address_idx = address_list.currentRow()
      address = self.watch_only_wallet.ui_addresses[address_idx]
      self.address_name_text.setText(address.label)
      self.address_name_text.setText(address.label)
      self.address_text.setText("Receiving Address: {}".format(str(address)))
      self.key_path_text.setText("Key Path: 0/0/0/0")

      buffer = BytesIO()
      image = qrcode.make(str(address))
      image.save(buffer, "PNG")
      qr_code_pixmap = QPixmap()
      qr_code_pixmap.loadFromData(buffer.getvalue(), "PNG")
      self.qr_code.setPixmap(qr_code_pixmap)





