import json
import os
from typing import List, Tuple

from bitcointx.wallet import CCoinExtPubKey as ExtPubKey

from models.hardware_wallet_init_dto import HardwareWalletInitDTO
from models.hd_key_path import HDKeyPath


class HardwareWalletFile:
    PATH = "hardware_wallet.json"

    def __new__(cls, hardware_wallet_init_data: HardwareWalletInitDTO):
        master_fingerprint = hardware_wallet_init_data.master_fingerprint
        candidate_wallets = hardware_wallet_init_data.candidate_wallets
        init_wallet_data = {
          "master_fingerprint": hardware_wallet_init_data.master_fingerprint.hex(),
          "recovery_phrase_length": hardware_wallet_init_data.recovery_phrase_length,
          "wallet_xpubs": [str(xpub) for xpub, _ in candidate_wallets],
          "key_paths": {str(xpub): str(keypath) for xpub, keypath in candidate_wallets},
        }
        with open(cls.PATH, 'w') as init_wallet_file:
          json.dump(init_wallet_data, init_wallet_file, indent=4)

    @classmethod
    def exists(cls):
        return os.path.exists(cls.PATH)

    @classmethod
    def load_candidate_wallets(cls) -> List[Tuple[ExtPubKey, HDKeyPath]]:
        with open(cls.PATH, "r") as hardware_wallet_file:
            init_wallet_json = json.load(hardware_wallet_file)
            candidate_wallets = []
            for xpub_str in init_wallet_json["wallet_xpubs"]:
                xpub = ExtPubKey(xpub_str)
                keypath = HDKeyPath(init_wallet_json["key_paths"][xpub_str])
                candidate_wallet = xpub, keypath
                candidate_wallets.append(candidate_wallet)

        return candidate_wallets

    @classmethod
    def load_master_fingerprint(cls) -> bytes:
        with open(cls.PATH, "r") as hardware_wallet_file:
            init_wallet_json = json.load(hardware_wallet_file)
        return bytes.fromhex(init_wallet_json["master_fingerprint"])


    @classmethod
    def load_recovery_phrase_length(cls) -> int:
      with open(cls.PATH, "r") as hardware_wallet_file:
        hardware_wallet_json = json.load(hardware_wallet_file)
      return hardware_wallet_json["recovery_phrase_length"]
