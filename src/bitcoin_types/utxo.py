from typing import Union

from bitcointx.core import (
    b2x,
    x,
    CMutableTxIn as TxIn,
    CMutableTxOut as TxOut,
    COutPoint as OutPoint
)
from bitcointx.core.script import CScript as Script

from bitcointx.wallet import (
  CCoinAddress as Address,
  P2PKHCoinAddress as P2PKHAddress,
  P2SHCoinAddress as P2SHAddress,
  P2WPKHCoinAddress as P2WPKHAddress,
  T_CCoinAddress as AddressType,
)

from bitcoin_types.block import Block
from constants.confirmation_constants import MINIMUM_CONFIRMATIONS
from constants.transaction_size_constants import (
    P2PKH_SPEND_BYTES,
    NP2WPKH_SPEND_BYTES,
    P2WPKH_SPEND_BYTES,
    P2PKH_OUTPUT_BYTES,
    NP2WPKH_OUTPUT_BYTES,
    P2WPKH_OUTPUT_BYTES
)

class Utxo():
    tx_in: TxIn
    tx_out: TxOut
    block: Block
    address: str
    is_awaiting_spend: bool = False


    def __init__(self, block: Block, tx_in: TxIn, tx_out: TxOut):
        self.tx_in = tx_in
        self.tx_out = tx_out
        self.block = block

    def __eq__(self, other):
        return self.tx_in == other.tx_in and self.tx_out == other.tx_out

    @property
    def value(self):
        return self.tx_out.nValue

    @property
    def prevout(self):
        return self.tx_in.prevout


    def is_spendable(self, current_block: Block):
        return self.confirmations(current_block) >= MINIMUM_CONFIRMATIONS and not self.is_awaiting_spend


    def is_pending_confirmation(self, current_block: Block):
        return self.confirmations(current_block) < MINIMUM_CONFIRMATIONS and not self.is_awaiting_spend


    def confirmations(self, current_block: Block):
        return (current_block.number - self.block.number) + 1

    #todo: do this without constants or verify these constants myself
    @staticmethod
    def spend_size(origin_address: Union[Address, "WalletAddress"]):
        from bitcoin_types.wallet_address import WalletAddress
        if isinstance(origin_address, WalletAddress):
            origin_address = origin_address._address

        if isinstance(origin_address, P2PKHAddress):
            return P2PKH_SPEND_BYTES
        elif isinstance(origin_address, P2SHAddress):
            return NP2WPKH_SPEND_BYTES
        elif isinstance(origin_address, P2WPKHAddress):
            return P2WPKH_SPEND_BYTES
        else:
            raise Exception

    # todo: do this without constants or verify these constants myself
    # taken from https://bitcoin.stackexchange.com/questions/66428/what-is-the-size-of-different-bitcoin-transaction-types
    @staticmethod
    def output_size(destination_address: Union[Address, "WalletAddress"]):
        from bitcoin_types.wallet_address import WalletAddress
        if isinstance(destination_address, WalletAddress):
            destination_address = destination_address._address

        if isinstance(destination_address, P2PKHAddress):
            return P2PKH_OUTPUT_BYTES
        elif isinstance(destination_address, P2SHAddress):
            return NP2WPKH_OUTPUT_BYTES
        elif isinstance(destination_address, P2WPKHAddress):
            return P2WPKH_OUTPUT_BYTES
        else:
            raise Exception
            #todo: what if i am sending to an "exotic" address type?



    def to_json(self):
        return {
            "is_awaiting_spend": self.is_awaiting_spend,
            "block": self.block.to_json(),
            "prevout": {
                "hash": b2x(self.prevout.hash),
                "n": self.prevout.n
            },
            "value": self.value,
            "script_pubkey": b2x(self.tx_out.scriptPubKey)
        }


    @classmethod
    def from_json(cls, json: dict):
        return cls(
            Block.from_json(json["block"]),
            TxIn(
                OutPoint(
                    x(json["prevout"]["hash"]),
                    json["prevout"]["n"]
                )
            ),
            TxOut(
                json["value"],
                x(json["script_pubkey"])
            )
        )
