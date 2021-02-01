from bitcointx.core import coins_to_satoshi, satoshi_to_coins
from bitcointx.wallet import CCoinAddress as ExternalAddress
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from serial import SerialException

from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from controllers.main_controller import MainController
from errors.tx_broadcast_api_error import TxBroadcastAPIError
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import Network
from utils.coin_selection_utils import map_coin_selection_to_utxos
from views.error_modal_view import ErrorMessage, ErrorModal
from views.send.fee_selection_form_view import FeeSelectionForm
from views.send.send_amount_form_view import SendAmountForm
from views.send.target_address_form_view import TargetAddressForm


class SendView(QWidget):
    TESTNET_TX_URL = "https://live.blockcypher.com/btc-testnet/tx/{txid}"
    MAINNET_TX_URL ="https://live.blockcypher.com/btc/tx/{txid}"

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
        self.send_button = QPushButton("Send transaction")
        self.send_button.clicked.connect(self.handle_click_send_button)
        self.send_button.setEnabled(False)
        self.send_button.setToolTip("Connect hardware wallet")
        self.send_button_form.layout.addWidget(self.send_button)

        self.layout.addWidget(self.target_address_form)
        self.layout.addWidget(self.fee_selection_form)
        self.layout.addWidget(self.send_amount_form)
        self.layout.addWidget(self.send_button_form)

        self.init_event_handlers()



    def init_event_handlers(self):
        self.controller.hardware_wallet_initialized.connect(
            self.handle_hardware_wallet_initialized
        )
        self.controller.hardware_wallet_loaded.connect(
            self.handle_hardware_wallet_loaded
        )
        self.controller.serial_client.connection.connect(
            self.handle_serial_connection_change
        )


    @property
    def address_input_text(self):
        return self.target_address_form.target_address_input.text().strip()


    def address_is_not_none(self, address_str: str) -> bool:
        return bool(len(address_str))


    def address_is_valid(self, address_str: str) -> bool:
        try:
            address = ExternalAddress(address_str)
            return True
        except Exception:
            return False


    @property
    def spend_amount(self):
        return float(self.send_amount_form.send_amount_input.text())

    def set_spend_amount(self, amount: float):
        self.send_amount_form.send_amount_input.setText(str(amount))


    @property
    def priority_fee_selected(self):
        return self.fee_selection_form.priority_fee_button.isChecked()


    def get_max_spend_btc(self) -> float:
        address_str = self.address_input_text
        address = (
            ExternalAddress(address_str)
            if self.address_is_valid(address_str) else None
        )
        max_spend_satosis = self.controller.get_max_possible_spend(
            self.priority_fee_selected, address
        )
        return satoshi_to_coins(max_spend_satosis)

    def select_coins(self, address: ExternalAddress):
        target_value = coins_to_satoshi(self.spend_amount, False)
        return self.controller.select_coins(
            target_value, address, self.priority_fee_selected)

    def attempt_spend(self, address: ExternalAddress, coin_selection: CoinSelection):
        try:
            tx_id = self.controller.orchestrate_spend(address, coin_selection)
            self.send_button.setEnabled(True)
            if not tx_id:
                self.error_modal.show(ErrorMessage.TX_REJECTED)
            else:
                self.show_transaction_url(tx_id)

        except SerialException:
            self.error_modal.show(ErrorMessage.SERIAL_DISCONNECT)
        except TxBroadcastAPIError:
            self.error_modal.show(ErrorMessage.TX_BROADCAST_FAILED)
        finally:
            self.send_button.setEnabled(True)



    def show_transaction_url(self, tx_id: str):
        if self.controller.network == Network.TESTNET:
            tx_url = self.TESTNET_TX_URL
        elif self.controller.network == Network.MAINNET:
            tx_url = self.MAINNET_TX_URL
        tx_url = QUrl(tx_url.format(tx_id))
        QDesktopServices.openUrl(tx_url)






    ############################ Event Handlers ##############################

    def handle_click_send_button(self):
        self.send_button.setEnabled(False)
        address_str = self.address_input_text
        if not self.address_is_not_none(address_str):
            self.send_button.setEnabled(True)
            self.error_modal.show(ErrorMessage.NO_ADDRESS)
            return
        elif not self.address_is_valid(address_str):
            self.send_button.setEnabled(True)
            self.error_modal.show(ErrorMessage.INVALID_ADDRESS)
            return

        address = ExternalAddress(address_str)
        selection = self.select_coins(address)
        if selection.outcome == selection.Outcome.INSUFFICIENT_FUNDS:
            self.send_button.setEnabled(True)
            self.error_modal.show(ErrorMessage.INSUFFICIENT_FUNDS)
            return
        elif selection.outcome == selection.Outcome.INSUFFICIENT_FUNDS_AFTER_FEES:
            self.send_button.setEnabled(True)
            self.error_modal.show(ErrorMessage.INSUFFICIENT_FUNDS_AFTER_FEES)
            return
        elif selection.outcome == selection.Outcome.INVALID_SPEND:
            self.send_button.setEnabled(True)
            self.error_modal.show(ErrorMessage.INVALID_SPEND)
            return

        # spinner or something
        self.attempt_spend(address, selection)


    def handle_click_send_max_amount_button(self):
        max_spend_btc = self.get_max_spend_btc()
        self.set_spend_amount(max_spend_btc)


    @pyqtSlot(bool)
    def handle_serial_connection_change(self, is_connected):
        if not is_connected:
            self.send_button.setEnabled(False)
            self.send_button.setToolTip("Connect hardware wallet")


    def handle_hardware_wallet_loaded(self):
        self.send_button.setEnabled(True)
        self.send_button.setToolTip("")


    def handle_hardware_wallet_initialized(self):
        self.send_button.setEnabled(True)
        self.send_button.setToolTip("")
