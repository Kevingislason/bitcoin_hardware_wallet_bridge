from typing import List, Tuple

from bitcointx.wallet import CCoinExtPubKey as ExtPubKey

from bitcoin_types.hd_key_path import HDKeyPath
from persistence.hardware_wallet_file import HardwareWalletFile


class HardwareWalletInitDTO():
  master_fingerprint: bytes
  candidate_wallets: List[Tuple[ExtPubKey, HDKeyPath]]

  def __init__(self, serial_payload):
      master_fingerprint = bytes.fromhex(serial_payload["master_fingerprint"])
      raw_xpubs: List[bytes] = serial_payload["wallet_xpubs"]
      candidate_wallets = []
      for raw_xpub in raw_xpubs:
          xpub = ExtPubKey(raw_xpub)
          keypath = HDKeyPath(serial_payload["key_paths"][raw_xpub])
          candidate_wallets.append((xpub, keypath))
      self.master_fingerprint = master_fingerprint
      self.candidate_wallets = candidate_wallets


