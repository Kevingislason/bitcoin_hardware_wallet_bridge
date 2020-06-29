from typing import List
from types.utxo import UTXO
from types.address import Address


class WatchOnlyWallet():
    utxos: List[UTXO]
    addresses: List[Address]

    def get_balance():
        pass
