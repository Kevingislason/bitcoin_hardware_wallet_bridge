from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import bcrypt
from functools import partial


class WalletView(QGridLayout):
    def __init__(self, set_layout):
        super().__init__()
        self.set_layout = set_layout
