from typing import Optional

from constants.genesis_block_constants import (MAINNET_GENESIS_HASH,
                                               TESTNET_GENESIS_HASH)
from persistence.config import Config, Network


class Block:
    hash: str
    number: int
    prev_hash: str

    def __init__(self, hash: str, number: int, prev_hash: Optional[str] = None):
        self.hash = hash
        self.number = number
        self.prev_hash = prev_hash


    def __eq__(self, other):
      return self.hash == other.hash


    @classmethod
    def genesis_block(cls):
      network =  Config.get_network()
      if network == Network.MAINNET:
        blockhash = MAINNET_GENESIS_HASH
      elif network == Network.TESTNET:
        blockhash = TESTNET_GENESIS_HASH
      return cls(blockhash, 0)

    def to_json(self):
      return {
        "hash": self.hash,
        "number": self.number,
        "prev_hash": self.prev_hash
      }

    @classmethod
    def from_json(cls, json: dict):
      return cls(json["hash"], json["number"], json["prev_hash"])
