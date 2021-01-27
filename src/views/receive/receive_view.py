from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from views.receive.address_detail_view import AddressDetailView
from views.receive.address_list_view import AddressListView

class ReceiveView(QWidget):
    controller: MainController
    watch_only_wallet: WatchOnlyWallet

    def __init__(self, controller: MainController, watch_only_wallet: WatchOnlyWallet):

      super().__init__()
      self.controller = controller
      self.watch_only_wallet = watch_only_wallet
      self.layout = QHBoxLayout(self)
      self.setLayout(self.layout)


      self.address_list = AddressListView(controller, watch_only_wallet)
      self.address_details = AddressDetailView(controller, watch_only_wallet)

      self.address_list.list.itemSelectionChanged.connect(
          partial(
            self.address_details.handle_address_changed,
            self.address_list.list
          )
      )

      self.layout.addWidget(self.address_list)
      self.layout.addWidget(self.address_details)


