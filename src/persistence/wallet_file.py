from enum import Enum
from typing import List, TypeVar
import json
import os

from bitcointx.wallet import (
    T_CCoinAddress as AddressType,
    CCoinExtPubKey as ExtPubKey,
    T_CCoinAddress as AddressType,
    T_P2PKHCoinAddress,
    T_P2SHCoinAddress,
    T_P2WPKHCoinAddress
)

from bitcoin_types.block import Block
from bitcoin_types.wallet_address import WalletAddress
from bitcoin_types.tx_in import TxIn
from models.watch_only_wallet import WatchOnlyWallet


#todo: encrypt
class WalletFile:
    PATH = "watch_only_wallet.json"


    def __new__(cls, wallet: WatchOnlyWallet):
        wallet_data = {
        "master_xpub": str(wallet.wallet_xpub),
        "address_type": str(wallet.address_type)[1:],
        "current_block": wallet.current_block.to_json(),
        "external_addresses": [address.to_json() for address in wallet.external_addresses.values()],
        "change_addresses": [address.to_json() for address in wallet.change_addresses.values()],
        }
        #os.remove(cls.PATH)
        with open(cls.PATH, "w") as wallet_file:
            json.dump(wallet_data, wallet_file, indent=4)


    @classmethod
    def exists(cls) -> bool:
        return os.path.exists(cls.PATH)


    @classmethod
    def save(cls, wallet: WatchOnlyWallet):
        external_addresses_json = [address.to_json() for address in wallet.external_addresses.values()]
        change_addresses_json = [address.to_json() for address in wallet.change_addresses.values()]

        with open(cls.PATH, 'r') as wallet_file:
            wallet_json = json.load(wallet_file)
            wallet_json["external_addresses"] = external_addresses_json
            wallet_json["change_addresses"] = change_addresses_json
            wallet_json["current_block"] = wallet.current_block.to_json()
        os.remove(cls.PATH)
        with open(cls.PATH, 'w') as wallet_file:
            json.dump(wallet_json, wallet_file, indent=4)


    @classmethod
    def load(cls):
        with open(cls.PATH, "r") as rf:
            wallet_json = json.load(rf)
            master_xpub = ExtPubKey(wallet_json["master_xpub"])
            # dumb hack to get the right address type class from bitcoin tx from a string
            # todo: at least make a util method for this
            address_type = globals()[wallet_json["address_type"]]
            current_block = Block.from_json(wallet_json["current_block"])
            external_addresses = wallet_json["external_addresses"]
            change_addresses = wallet_json["change_addresses"]

            external_addresses = [
                WalletAddress(
                    master_xpub,
                    address_type,
                    child_number,
                    False,
                    address["was_recovered"],
                    address["is_fresh"],
                    [TxIn.from_json(tx_in) for tx_in in address["tx_ins"]],
                    address.get("label")
                )
                for child_number, address in enumerate(external_addresses)
            ]

            change_addresses = [
                WalletAddress(
                    master_xpub,
                    address_type,
                    child_number,
                    True,
                    address["was_recovered"],
                    address["is_fresh"],
                    [TxIn.from_json(tx_in) for tx_in in address["tx_ins"]]
                )
                for child_number, address in enumerate(change_addresses)
            ]

            return (master_xpub, address_type, current_block, external_addresses, change_addresses)
