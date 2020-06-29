from network.network_client_interface import NetworkClientInterface
from errors.block_explorer_api_error import BlockExplorerAPIError
import requests


class BlockExplorerClient(NetworkClientInterface):

    def get_utxos(self, addresses):
        utxos = []

        # Get up to 1000 utxos for each address
        response = requests.get(
            "https://blockchain.info/unspent?active="
            + "|".join(addresses)
            + "&limit=1000"
        )
        if response.status_code != 200:
            raise BlockExplorerAPIError(response.status_code)

        uxtos = response.json()["unspent_outputs"]
        # todo: convert to UXTO type
        return utxos
