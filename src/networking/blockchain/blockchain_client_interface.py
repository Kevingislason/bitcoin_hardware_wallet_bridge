from abc import ABCMeta, abstractmethod
from typing import List

from models.tx_in import TxIn


class BlockchainClientInterface():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_txins(self, address_list: List[str]) -> List[TxIn]:
        pass
