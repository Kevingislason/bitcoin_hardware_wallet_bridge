from abc import ABCMeta, abstractmethod
from typing import List

from bitcoin_types.wallet_address import WalletAddress
from bitcoin_types.utxo import Utxo


class BlockchainClientInterface():
    __metaclass__ = ABCMeta

    # @abstractmethod
    # def get_txins(self, address_list: List[str]) -> List[Utxo]:
    #     pass

    # @abstractmethod
    # def address_has_been_used(self, address: WalletAddress) -> bool:
    #     pass


