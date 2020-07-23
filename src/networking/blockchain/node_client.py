from typing import List

from networking.blockchain.blockchain_client_interface import (
    BlockchainClientInterface
)
from models.tx_in import TxIn


class NodeClient(BlockchainClientInterface):
    def get_txins(self, addresses) -> List[TxIn]:
        pass
