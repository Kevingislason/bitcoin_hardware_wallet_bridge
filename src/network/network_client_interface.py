from abc import ABCMeta, abstractmethod
from typing import List


class NetworkClientInterface():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_utxos(self, address_list: List[str]) -> List[int]:
        pass
