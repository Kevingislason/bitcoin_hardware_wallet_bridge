from bitcointx.core import CMutableTxIn, COutPoint as OutPoint
from bitcointx.core.script import CScript as Script

from bitcoin_types.block import Block
from constants.confirmation_constants import MINIMUM_CONFIRMATIONS

class TxIn(CMutableTxIn):
    satoshi_value: int
    block: Block
    is_awaiting_spend: bool = False

    def __init__(self, satoshi_value: int, block: Block, *args, **kwargs):
        super(TxIn, self).__init__(*args, **kwargs)
        self.satoshi_value = satoshi_value
        self.block = block


    def is_spendable(self, current_block: Block):
        return self.confirmations(current_block) >= MINIMUM_CONFIRMATIONS and not self.is_awaiting_spend


    def is_pending_confirmation(self, current_block: Block):
        return self.confirmations(current_block) < MINIMUM_CONFIRMATIONS and not self.is_awaiting_spend


    def confirmations(self, current_block: Block):
        return (current_block.number - self.block.number) + 1


    def to_json(self):
        return {
            "satoshi_value": self.satoshi_value,
            "is_awaiting_spend": self.is_awaiting_spend,
            "block": self.block.to_json(),
            "prevout": {
                "hash": self.prevout.hash.hex(),
                "n": self.prevout.n
            }
        }


    @classmethod
    def from_json(cls, tx_in_json: dict):
        return cls(
            tx_in_json["satoshi_value"],
            Block.from_json(tx_in_json["block"]),
            OutPoint(
                bytes.fromhex(tx_in_json["prevout"]["hash"]),
                tx_in_json["prevout"]["n"]
            )
        )




# class CMutableTxIn(CTxIn, mutable_of=CTxIn, next_dispatch_final=True):
    # prevout: WriteableField[CMutableOutPoint]  # type: ignore
    # scriptSig: WriteableField[script.CScript]
    # nSequence: WriteableField[int]
