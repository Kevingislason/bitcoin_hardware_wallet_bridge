from collections import OrderedDict
from itertools import chain
from typing import List, MutableMapping, Optional

from bitcointx.wallet import CCoinExtPubKey as ExtPubKey
from PyQt5.QtCore import QObject, pyqtSignal

from models.block import Block
from models.utxo import Utxo
from models.wallet_address import WalletAddress
from constants.confirmation_constants import MINIMUM_CONFIRMATIONS
from constants.wallet_recovery_constants import EXTERNAL_GAP_LIMIT


class WatchOnlyWallet(QObject):
    xpub: ExtPubKey
    base_keypath: str
    external_addresses: MutableMapping[str, WalletAddress]
    change_addresses: MutableMapping[str, WalletAddress]
    current_block: Block
    spendable_balance_satoshis: int
    incoming_balance_satoshis: int

    spendable_balance_satoshis_changed = pyqtSignal(int)
    incoming_balance_satoshis_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.xpub = None
        self.master_fingerprint = None
        self.base_keypath = None
        self.current_block = None
        self.spendable_balance_satoshis = 0
        self.incoming_balance_satoshis = 0
        self.external_addresses = OrderedDict()
        self.change_addresses = OrderedDict()

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
    def last_change_address(self):
        return next(reversed(self.change_addresses.items()))[1]

    @property
    def has_reached_gap_limit(self) -> bool:
        if len(self.external_addresses) < EXTERNAL_GAP_LIMIT:
            return False
        for address in list(reversed(self.external_addresses.values()))[:EXTERNAL_GAP_LIMIT]:
            if not address.is_fresh:
                return False
        return True


    def refresh_balances(self):
        self.incoming_balance_satoshis = sum(
            utxo.value
            for address in self.addresses
            for utxo in address.utxos
            if utxo.is_incoming(self.current_block)
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
        self.incoming_balance_satoshis_changed.emit(
            self.incoming_balance_satoshis
        )
