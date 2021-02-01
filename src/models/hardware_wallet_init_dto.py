from typing import List, Tuple

from bitcointx.wallet import CCoinExtPubKey as ExtPubKey

from models.hd_key_path import HDKeyPath


class HardwareWalletInitDTO():
    master_fingerprint: bytes
    recovery_phrase_length: int
    candidate_wallets: List[Tuple[ExtPubKey, HDKeyPath]]

    def __init__(self, serial_payload):
        self.master_fingerprint = bytes.fromhex(serial_payload["master_fingerprint"])
        self.recovery_phrase_length = serial_payload["recovery_phrase_length"]
        raw_xpubs: List[bytes] = serial_payload["wallet_xpubs"]
        self.candidate_wallets = []
        for raw_xpub in raw_xpubs:
            xpub = ExtPubKey(raw_xpub)
            keypath = HDKeyPath(serial_payload["key_paths"][raw_xpub])
            self.candidate_wallets.append((xpub, keypath))
