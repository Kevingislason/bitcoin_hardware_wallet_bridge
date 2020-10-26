from typing import List

from bitcointx.wallet import (
  CCoinAddress,
  CPubKey as PubKey,
  CCoinExtPubKey as ExtPubKey,
  P2PKHCoinAddress as P2PKHAddress,
  P2SHCoinAddress as P2SHAddress,
  P2WPKHCoinAddress as P2WPKHAddress,
  T_CCoinAddress as AddressType,
  T_P2PKHCoinAddress as P2PKHAddressType,
  T_P2SHCoinAddress as P2SHAddressType,
  T_P2WPKHCoinAddress as P2WPHKAddressType
)
from bitcointx.core.serialize import Hash160
from bitcointx.core.script import CScript, OP_HASH160, OP_EQUAL

from bitcoin_types.history_event import HistoryEvent
from bitcoin_types.tx_in import TxIn



class WalletAddress:
    _address: CCoinAddress
    _tx_ins: List[TxIn]
    child_number: int
    was_recovered: bool
    is_fresh: bool

    def __init__(self,
                 wallet_xpub: ExtPubKey,
                 address_type: AddressType,
                 child_number: int,
                 is_change_address: bool = False,
                 was_recovered: bool = False,
                 is_fresh: bool = True,
                 tx_ins: List[TxIn] = None,
                 label: str = None
                ):

        if is_change_address:
          chain_xpub = wallet_xpub.derive(1)
        else:
          chain_xpub = wallet_xpub.derive(0)
        address_pubkey = chain_xpub.derive(child_number).pub

        if address_type is P2PKHAddressType:
            address = P2PKHAddress.from_pubkey(address_pubkey)
        elif address_type is P2WPHKAddressType:
            address = P2WPKHAddress.from_pubkey(address_pubkey)
        elif address_type is P2SHAddressType:
            address = WalletAddress.make_wrapped_segwit_address(address_pubkey)
        else:
            raise Exception

        self._address = address
        self.child_number = child_number
        self.is_fresh = is_fresh
        self.was_recovered = was_recovered
        if tx_ins:
            self.tx_ins = tx_ins
        else:
            self.tx_ins = []

        self.label = label

    def __str__(self):
        return str(self._address)


    @property
    def tx_ins(self) -> List[TxIn]:
        return self._tx_ins

    @tx_ins.setter
    def tx_ins(self, tx_ins: List[TxIn]):
        self._tx_ins = tx_ins
        if tx_ins:
          self.is_fresh = False

    def to_json(self):
        return {
            "was_recovered": self.was_recovered,
            "is_fresh": self.is_fresh,
            "tx_ins": [tx_in.to_json() for tx_in in self.tx_ins],
            "label": self.label
        }



    # Make a P2WPKH address wrapped in P2SH address (https://wiki.trezor.io/P2WPKH-in-P2SH)
    @staticmethod
    def make_wrapped_segwit_address(address_pubkey) -> CCoinAddress:
        redeem_script = P2WPKHAddress.from_pubkey(address_pubkey).to_scriptPubKey()
        redeem_script_hash = Hash160(redeem_script)
        script_pubkey = CScript([OP_HASH160, redeem_script_hash, OP_EQUAL])
        return P2SHAddress.from_scriptPubKey(script_pubkey)





