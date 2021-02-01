from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class FeeSelectionForm(QWidget):
    def __init__(self):
      super().__init__()

      self.layout = QHBoxLayout()
      self.setLayout(self.layout)

      self.fee_selection_label = QLabel("Fee rate:")
      self.fee_selection_label.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
      self.fee_selection_label.size_policy.setHorizontalStretch(1)
      self.fee_selection_label.setSizePolicy(self.fee_selection_label.size_policy)

      self.fee_buttons_container = QWidget()
      self.fee_buttons_container.layout = QHBoxLayout()
      self.fee_buttons_container.setLayout(self.fee_buttons_container.layout)
      self.fee_buttons_container.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
      self.fee_buttons_container.size_policy.setHorizontalStretch(2)
      self.fee_buttons_container.setSizePolicy(self.fee_buttons_container.size_policy)
      self.normal_fee_button = QRadioButton("Normal")
      self.priority_fee_button = QRadioButton("Priority")
      self.normal_fee_button.setChecked(True)
      self.fee_buttons_container.layout.addWidget(self.normal_fee_button)
      self.fee_buttons_container.layout.addWidget(self.priority_fee_button)

      self.fee_selection_spacer = QLabel("")
      self.fee_selection_spacer.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
      self.fee_selection_spacer.size_policy.setHorizontalStretch(6)
      self.fee_selection_spacer.setSizePolicy(self.fee_selection_spacer.size_policy)

      self.layout.addWidget(self.fee_selection_label)
      self.layout.addWidget(self.fee_buttons_container)
      self.layout.addWidget(self.fee_selection_spacer)
