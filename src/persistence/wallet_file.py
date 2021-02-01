import json
import os
from typing import List

from bitcointx.core import b2x, x
from bitcointx.wallet import CCoinExtPubKey as ExtPubKey
from bitcointx.wallet import (P2PKHCoinAddress, P2SHCoinAddress,
                              P2WPKHCoinAddress)

from models.block import Block
from models.hd_key_path import HDKeyPath
from models.utxo import Utxo
from models.wallet_address import WalletAddress
from models.watch_only_wallet import WatchOnlyWallet


class WalletFile:
    PATH = "watch_only_wallet.json"


    def __new__(cls, wallet: WatchOnlyWallet):
        wallet_data = {
            "wallet_xpub": str(wallet.xpub),
            "master_fingerprint": b2x(wallet.master_fingerprint),
            "base_keypath": str(wallet.base_keypath),
            "current_block": wallet.current_block.to_json(),
            "external_addresses": [
                address.to_json() for address in wallet.external_addresses.values()
            ],
            "change_addresses": [
                address.to_json() for address in wallet.change_addresses.values()
            ],
        }
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
            wallet_xpub = ExtPubKey(wallet_json["wallet_xpub"])
            master_fingerprint = x(wallet_json["master_fingerprint"])
            base_keypath = HDKeyPath(wallet_json["base_keypath"])
            current_block = Block.from_json(wallet_json["current_block"])
            raw_external_addresses = wallet_json["external_addresses"]
            raw_change_addresses = wallet_json["change_addresses"]

            external_addresses = [
                WalletAddress(
                    wallet_xpub,
                    base_keypath,
                    child_number,
                    False,
                    address["was_recovered"],
                    address["is_fresh"],
                    [Utxo.from_json(utxo) for utxo in address["utxos"]],
                    address.get("label")
                )
                for child_number, address in enumerate(raw_external_addresses)
            ]

            change_addresses = [
                WalletAddress(
                    wallet_xpub,
                    base_keypath,
                    child_number,
                    True,
                    address["was_recovered"],
                    address["is_fresh"],
                    [Utxo.from_json(utxo) for utxo in address["utxos"]]
                )
                for child_number, address in enumerate(raw_change_addresses)
            ]

            return (wallet_xpub, master_fingerprint, base_keypath, current_block, external_addresses, change_addresses)
