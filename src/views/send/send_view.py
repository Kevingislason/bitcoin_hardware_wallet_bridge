
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from bitcointx.wallet import CCoinAddress as ExternalAddress
from bitcointx.core import satoshi_to_coins, coins_to_satoshi


from controllers.main_controller import MainController

from models.watch_only_wallet import WatchOnlyWallet
from utils.coin_selection_utils import map_coin_selection_to_utxos
from views.send.send_amount_form_view import SendAmountForm
from views.send.fee_selection_form_view import FeeSelectionForm
from views.send.target_address_form_view import TargetAddressForm
from views.send.error_modal_view import ErrorModal, ErrorMessage


class SendView(QWidget):
    def __init__(self, controller: MainController, watch_only_wallet: WatchOnlyWallet):

        super().__init__()

        self.controller = controller
        self.watch_only_wallet = watch_only_wallet

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignVCenter)
        self.layout.setSpacing(40)
        self.setLayout(self.layout)
        self.size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setSizePolicy(self.size_policy)

        self.error_modal = ErrorModal()

        self.target_address_form = TargetAddressForm()

        self.fee_selection_form = FeeSelectionForm()

        self.send_amount_form = SendAmountForm()
        self.send_amount_form.send_max_amount_button.clicked.connect(
            self.handle_click_send_max_amount_button
        )

        self.send_button_form = QWidget()
        self.send_button_form.layout = QVBoxLayout()
        self.send_button_form.layout.setAlignment(Qt.AlignCenter)
        self.send_button_form.setLayout(self.send_button_form.layout)
        self.send_button = QPushButton("Send Transaction")
        self.send_button.clicked.connect(self.handle_click_send_button)
        self.send_button_form.layout.addWidget(self.send_button)

        self.layout.addWidget(self.target_address_form)
        self.layout.addWidget(self.fee_selection_form)
        self.layout.addWidget(self.send_amount_form)
        self.layout.addWidget(self.send_button_form)


    def handle_click_send_max_amount_button(self):
        try:
            address = ExternalAddress(self.target_address_form.target_address_input.text().strip())
        except Exception:
            address = None
        is_priority = self.fee_selection_form.priority_fee_button.isChecked()
        max_spend = satoshi_to_coins(
            self.controller.get_max_possible_spend(is_priority, address)
        )
        self.send_amount_form.send_amount_input.setText(str(max_spend))


    def handle_click_send_button(self):
        # Validate address
        address_str = self.target_address_form.target_address_input.text().strip()
        if not address_str:
            self.error_modal.show(ErrorMessage.NO_ADDRESS)
            return
        try:
            address = ExternalAddress(self.target_address_form.target_address_input.text().strip())
        except Exception:
            self.error_modal.show(ErrorMessage.INVALID_ADDRESS)
            return

        # Validate amount
        target_value = coins_to_satoshi(
            float(self.send_amount_form.send_amount_input.text()),
            False
        )
        is_priority = self.fee_selection_form.priority_fee_button.isChecked()
        selection = self.controller.select_coins(target_value, address, is_priority)

        if selection.outcome == selection.Outcome.INSUFFICIENT_FUNDS:
            self.error_modal.show(ErrorMessage.INSUFFICIENT_FUNDS)
            return
        elif selection.outcome == selection.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES:
            self.error_modal.show(ErrorMessage.INSUFFICIENT_FUNDS_AFTER_FEES)
            return
        elif selection.outcome == selection.Outcome.INVALID_SPEND:
            self.error_modal.show(ErrorMessage.INVALID_SPEND)
            return

        # Send Tx
        selected_utxos = map_coin_selection_to_utxos(selection, self.watch_only_wallet)
        tx = self.controller.assemble_tx(address, selected_utxos, target_value,
                                         selection.change_value)
        psbt = self.conrroller.assemble_psbt(transaction, selected_utxos)

        print("Okay")







