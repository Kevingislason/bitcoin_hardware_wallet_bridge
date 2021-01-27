import os
import json
from typing import List, Tuple

from bitcoin_types.hardware_wallet_init_dto import HardwareWalletInitDTO
from bitcoin_types.hd_key_path import HDKeyPath
from bitcointx.wallet import CCoinExtPubKey as ExtPubKey


class InitWalletFile:
    PATH = "init_wallet.json"

    def __new__(cls, hardware_wallet_init_data: HardwareWalletInitDTO):
      master_fingerprint = hardware_wallet_init_data.master_fingerprint
      candidate_wallets = hardware_wallet_init_data.candidate_wallets
      init_wallet_data = {
        "master_fingerprint": hardware_wallet_init_data.master_fingerprint.hex(),
        "wallet_xpubs": [str(xpub) for xpub, _ in candidate_wallets],
        "key_paths": {str(xpub): str(keypath) for xpub, keypath in candidate_wallets},
      }
      with open(cls.PATH, 'w') as init_wallet_file:
         json.dump(init_wallet_data, init_wallet_file, indent=4)

    @classmethod
    def exists(cls):
      return os.path.exists(cls.PATH)

    @classmethod
    def load(cls) -> Tuple[List[Tuple[ExtPubKey, HDKeyPath]], bytes]:
      with open(cls.PATH, "r") as init_wallet_file:
        init_wallet_json = json.load(init_wallet_file)

        candidate_wallets = []
        for xpub_str in init_wallet_json["wallet_xpubs"]:
          xpub = ExtPubKey(xpub_str)
          keypath = HDKeyPath(init_wallet_json["key_paths"][xpub_str])
          candidate_wallet = xpub, keypath
          candidate_wallets.append(candidate_wallet)

        master_fingerprint = bytes.fromhex(init_wallet_json["master_fingerprint"])

        return candidate_wallets, master_fingerprint
