import json
import requests

from errors.block_explorer_api_error import BlockExplorerAPIError
from networking.blockchain.blockchain_client_interface import BlockchainClientInterface


class BlockExplorerClient(BlockchainClientInterface):
    def get_tx_ins(self, addresses):
        utxos = []

        # Get up to 1000 utxos for each address
        response = requests.get(
            "https://blockchain.info/unspent?active="
            + "|".join(addresses)
            # + "&limit=1000"
        )
        if response.status_code != 200:
            raise BlockExplorerAPIError(response.status_code)

        utxos = json.loads(response.text)
        print(utxos)

        # todo: convert to UXTO type
        return utxos
