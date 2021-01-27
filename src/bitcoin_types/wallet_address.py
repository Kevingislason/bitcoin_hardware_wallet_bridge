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

from bitcoin_types.hd_key_path import HDKeyPath
from bitcoin_types.history_event import HistoryEvent
from bitcoin_types.utxo import Utxo
from constants.hd_key_path_constants import (
    bip_44_keypath,
    bip_49_keypath,
    bip_84_keypath,
    mainnet_keypath,
    testnet_keypath,
    first_account_keypath,
    external_chain_keypath,
    change_chain_keypath,
    paths_are_equal,
    BIP_KEYPATH_INDEX,
    CHANGE_KEYPATH_INDEX,
    CHILD_NUMBER_KEYPATH_INDEX,
    APP_BASE_KEYPATH_INDEX
)
from persistence.config import (
    Config,
    ChainParameters
)



class WalletAddress:
    _address: CCoinAddress
    _utxos: List[Utxo] #todo: make dict
    pub_key: PubKey
    key_path: HDKeyPath
    was_recovered: bool
    is_fresh: bool
    label: str

    def __init__(self,
                 wallet_xpub: ExtPubKey,
                 base_keypath: HDKeyPath,
                 child_number: int,
                 is_change_address: bool = False,
                 was_recovered: bool = False,
                 is_fresh: bool = True,
                 utxos: List[Utxo] = None,
                 label: str = None
                ):

        self._set_key_path(base_keypath, is_change_address, child_number)
        self._set_pubkey(wallet_xpub)
        self._derive_address()
        self.was_recovered = was_recovered
        self.is_fresh = is_fresh
        self.label = label
        if utxos:
            self.utxos = utxos
        else:
            self.utxos = []


    def __str__(self):
        return str(self._address)

    @property
    def utxos(self) -> List[Utxo]:
        return self._utxos

    @utxos.setter
    def utxos(self, utxos: List[Utxo]):
        self._utxos = utxos

        if self.utxos:
          self.is_fresh = False

        for utxo in self.utxos:
            utxo.address = str(self)

    @property
    def child_number(self) -> int:
        return self.key_path[CHILD_NUMBER_KEYPATH_INDEX]

    @property
    def is_change_address(self) -> bool:
        return self.key_path[CHANGE_KEYPATH_INDEX] == 1

    def to_scriptPubKey(self):
        return self._address.to_scriptPubKey()

    def to_redeemScript(self):
        if isinstance(self._address, P2SHAddress):
            return self.make_wrapped_segwit_redeem_script()
        else:
            return self._address.to_redeemScript()

    def to_json(self):
        return {
            "was_recovered": self.was_recovered,
            "is_fresh": self.is_fresh,
            "utxos": [utxo.to_json() for utxo in self.utxos],
            "label": self.label
        }

    def _set_key_path(self, base_keypath: HDKeyPath, is_change_address: bool, child_number: int):
        chain_params = Config.get_chain_parameters()
        if is_change_address:
            change_keypath = change_chain_keypath()
        else:
            change_keypath = external_chain_keypath()
        self.key_path = base_keypath + change_keypath + HDKeyPath(str(child_number))

    def _set_pubkey(self, wallet_xpub):
        app_keypath = self.key_path[APP_BASE_KEYPATH_INDEX:]
        self.pub_key = wallet_xpub.derive_path(app_keypath).pub

    def _derive_address(self):
        bip_keypath = HDKeyPath(self.key_path[:BIP_KEYPATH_INDEX])
        if bip_keypath == bip_44_keypath():
            self._address = P2PKHAddress.from_pubkey(self.pub_key)
        elif bip_keypath == bip_84_keypath():
            self._address = P2WPKHAddress.from_pubkey(self.pub_key)
        elif bip_keypath == bip_49_keypath():
            self._address = WalletAddress._make_wrapped_segwit_address(self.pub_key)
        else:
            raise Exception

    # Make a P2WPKH address wrapped in P2SH address (https://wiki.trezor.io/P2WPKH-in-P2SH)
    @staticmethod
    def _make_wrapped_segwit_address(address_pubkey) -> CCoinAddress:
        redeem_script = P2WPKHAddress.from_pubkey(address_pubkey).to_scriptPubKey()
        redeem_script_hash = Hash160(redeem_script)
        script_pubkey = CScript([OP_HASH160, redeem_script_hash, OP_EQUAL])
        return P2SHAddress.from_scriptPubKey(script_pubkey)

    @staticmethod
    def _make_wrapped_segwit_redeem_script(address_pubkey):
        # raise Exception("Unimplemented")
        return P2WPKHAddress.from_pubkey(address_pubkey).to_scriptPubKey()
