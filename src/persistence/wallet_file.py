from typing import List
import json
from os import path


class WalletFile:
    PATH = "watch_only_wallet.json"

    @classmethod
    def exists(cls) -> bool:
        return True  # path.exists(cls.PATH)

    @classmethod
    def get_public_keys(cls):  # -> List[ExtendedPublicKey]:
        pass
        # {
        #     script_pubkey
        #     derivation_path
        #     extended pubkey
        # }

        # todo: get/make this type
        # return [ExtendedPublicKey(row) for row in file]

    @classmethod
    def initialize_wallet_data_file(cls, master_xpubkey, master_xpubkey_path):
        wallet_data = {
            "master_xpubkey": {
                "value": master_xpubkey,
                "path": master_xpubkey_path
            },
            "child_xpubkeys": []
        }

        with open(WalletFile.PATH, "w") as outfile:
            json.dump(wallet_data, outfile)
