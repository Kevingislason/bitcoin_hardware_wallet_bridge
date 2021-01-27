from collections import OrderedDict
from typing import List, MutableMapping, Optional
from itertools import chain
from bitcointx.wallet import (
    CCoinExtPubKey as ExtPubKey,
    T_CCoinAddress as AddressType,
)
from PyQt5.QtCore import QObject, pyqtSignal


from bitcoin_types.block import Block
from bitcoin_types.utxo import Utxo
from bitcoin_types.wallet_address import WalletAddress
from constants.confirmation_constants import MINIMUM_CONFIRMATIONS

#todo: rename to wallet
#todo: move persistence into here from the controller
#todo: setter for add addresses and current block
class WatchOnlyWallet(QObject):

    # Wallet state
    xpub: ExtPubKey
    base_keypath: str
    external_addresses: MutableMapping[str, WalletAddress]
    change_addresses: MutableMapping[str, WalletAddress]
    current_block: Block
    spendable_balance_satoshis: int
    unspendable_balance_satoshis: int

    # Pyqt Signals
    unspendable_balance_satoshis_changed = pyqtSignal(int)
    spendable_balance_satoshis_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def load(
        self,
        xpub: ExtPubKey,
        master_fingerprint: bytes,
        base_keypath: str,
        current_block: Block,
        external_addresses: List[WalletAddress],
        change_addresses: List[WalletAddress]
    ):
        self.xpub = xpub
        self.master_fingerprint = master_fingerprint
        self.base_keypath = base_keypath
        self.current_block = current_block
        # Store change and external addresses in ordered dicts mapped to the address string
        self.external_addresses = OrderedDict(
            [(str(address), address) for address in external_addresses]
        )
        self.change_addresses =  OrderedDict(
            [(str(address), address) for address in change_addresses]
        )
        self.refresh_balances()

    def get_address(self, address_str: str):
        if self.external_addresses.get(address_str):
            return self.external_addresses[address_str]
        else:
            return self.change_addresses.get(address_str)

    @property
    def addresses(self) -> List[WalletAddress]:
        return list(chain(self.external_addresses.values(),self.change_addresses.values()))

    @property
    def ui_addresses(self) -> List[WalletAddress]:
        return [address for address in self.external_addresses.values() if not address.was_recovered][::-1]

    @property
    def utxos(self) -> List[Utxo]:
        return [
            utxo for address in self.addresses
            for utxo in address.utxos
        ]

    @property
    def last_change_address(self):
        return next(reversed(self.change_addresses.items()))[1]

    def refresh_balances(self):
        # Spendable_balance and unspendable_balance are what users see,
        # but the sum of all tx_ins in all wallet addresses are the source of truth.
        # This function lets us control when to reconcile the two,
        # so as to prevent the display balances from being too "jumpy"
        self.unspendable_balance_satoshis = sum(
            utxo.value
            for address in self.addresses
            for utxo in address.utxos
            if utxo.is_pending_confirmation(self.current_block)
        )
        self.spendable_balance_satoshis = sum(
            utxo.value
            for address in self.addresses
            for utxo in address.utxos
            if utxo.is_spendable(self.current_block)
        )

        self.spendable_balance_satoshis_changed.emit(
            self.spendable_balance_satoshis
        )
        self.unspendable_balance_satoshis_changed.emit(
            self.unspendable_balance_satoshis
        )
