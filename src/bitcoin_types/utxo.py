from typing import Union

from bitcointx.base58 import CBase58Data as Base58Data
from bitcointx.core import (
    b2lx,
    lx,
    CMutableTxIn as TxIn,
    CMutableTxOut as TxOut,
    COutPoint as OutPoint,
    CTransaction as Transaction

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
    tx_out: TxOut
    tx_in: TxIn
    transaction: Transaction
    block: Block
    address: str
    is_awaiting_spend: bool = False


    def __init__(self, block: Block, tx_in: TxIn, tx_out: TxOut):
        self.block = block
        self.tx_in = tx_in
        self.tx_out = tx_out

    def __eq__(self, other):
        return self.tx_in == other.tx_in and self.tx_out == other.tx_out

    @property
    def value(self):
        return self.tx_out.nValue

    @property
    def prevout(self):
        return self.tx_in.prevout

    @property
    def tx_hash(self):
        return b2lx(self.prevout.hash)

    @property
    def is_witness_utxo(self):
        return False #todo: idk what this means honestly


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
                "hash": b2lx(self.prevout.hash),
                "n": self.prevout.n
            },
            "value": self.value,
            "script_pubkey": b2lx(self.tx_out.scriptPubKey)
        }


    @classmethod
    def from_json(cls, json: dict):
        return cls(
            Block.from_json(json["block"]),
            TxIn(
                OutPoint(
                    lx(json["prevout"]["hash"]),
                    json["prevout"]["n"]
                )
            ),
            TxOut(
                json["value"],
                lx(json["script_pubkey"])
            )
        )
