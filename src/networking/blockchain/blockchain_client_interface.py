from abc import ABCMeta, abstractmethod
from typing import List


class BlockchainClientInterface():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_tx_ins(self, address_list: List[str]) -> List[int]:
        pass
