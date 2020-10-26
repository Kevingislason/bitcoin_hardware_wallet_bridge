# from typing import List

# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *

# from bitcoin_types.wallet_address import WalletAddress

# class AddressListItemView(QAbstractListModel):
#   addresses: List[WalletAddress]

#   def __init__(self):
#     QAbstractListModel.__init__(self)
#     self.items=[]
#     self.modelDict={}


#   def rowCount(self): #parent=QtCore.QModelIndex()):
#     return len(self.addresses)

#   def data(self, index, role):
#     if not index.isValid() or not (0<=index.row()<len(self.items)):
#       return QVariant()
#     if role==Qt.DisplayRole:
#       return

