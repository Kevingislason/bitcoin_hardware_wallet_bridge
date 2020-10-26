from collections import OrderedDict
from typing import List, MutableMapping, Optional
from itertools import chain
from bitcointx.wallet import (
    CCoinExtPubKey as ExtPubKey,
    T_CCoinAddress as AddressType,
)
from PyQt5.QtCore import QObject, pyqtSignal


from bitcoin_types.block import Block
from bitcoin_types.tx_in import TxIn
from bitcoin_types.wallet_address import WalletAddress
from constants.confirmation_constants import MINIMUM_CONFIRMATIONS

#todo: rename to wallet
#todo: move persistence into here from the controller
#todo: setter for add addresses and current block
class WatchOnlyWallet(QObject):

    # Wallet state
    wallet_xpub: ExtPubKey
    address_type: AddressType
    external_addresses: MutableMapping[str, WalletAddress]
    change_addresses: MutableMapping[str, WalletAddress]
    current_block: Block
    spendable_balance_satoshis: int
    unspendable_balance_satoshis: int

    # Pyqt Signals
    unspendable_balance_satoshis_changed = pyqtSignal(int)
    spendable_balance_satoshis_changed = pyqtSignal(int) #todo: rename to pending balance

    def __init__(self):
        super().__init__()

    def load(
        self,
        wallet_xpub: ExtPubKey,
        address_type: AddressType,
        current_block: Block,
        external_addresses: List[WalletAddress],
        change_addresses: List[WalletAddress]
    ):
        self.wallet_xpub = wallet_xpub
        self.address_type = address_type
        self.current_block = current_block
        # Store change and external addresses in ordered dicts mapped to the address string
        self.external_addresses = OrderedDict(
            [(str(address), address) for address in external_addresses]
        )
        self.change_addresses =  OrderedDict(
            [(str(address), address) for address in change_addresses]
        )

    #todo: make this into a property
    def addresses_iter(self) -> List[WalletAddress]:
        return chain(self.external_addresses.values(),self.change_addresses.values())

    @property
    def ui_addresses(self) -> List[WalletAddress]:
        return [address for address in self.external_addresses.values() if not address.was_recovered][::-1]

    def refresh_balances(self):
        # Spendable_balance and unspendable_balance are what users see,
        # but the sum of all tx_ins in all wallet addresses are the source of truth.
        # This function lets us control when to reconcile the two,
        # so as to prevent the display balances from being too "jumpy"
        self.unspendable_balance_satoshis = sum(
            tx_in.satoshi_value
            for address in self.addresses_iter()
            for tx_in in address.tx_ins
            if tx_in.is_pending_confirmation(self.current_block)
        )
        self.spendable_balance_satoshis = sum(
            tx_in.satoshi_value
            for address in self.addresses_iter()
            for tx_in in address.tx_ins
            if tx_in.is_spendable(self.current_block)
        )

        self.spendable_balance_satoshis_changed.emit(
            self.spendable_balance_satoshis
        )
        self.unspendable_balance_satoshis_changed.emit(
            self.unspendable_balance_satoshis
        )
