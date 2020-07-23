import json
import requests
from typing import List

from bitcointx.core import (
    COutPoint, lx
)

from errors.block_explorer_api_error import BlockExplorerAPIError
from networking.blockchain.blockchain_client_interface import BlockchainClientInterface
from models.tx_in import TxIn


class BlockExplorerClient(BlockchainClientInterface):
    def get_txins(self, addresses) -> List[TxIn]:
        # Get up to 1000 utxos for each address
        response = requests.get(
            "https://blockchain.info/unspent?active="
            + "|".join(addresses)
            + "&limit=1000"
        )
        if response.status_code != 200:
            raise BlockExplorerAPIError(response.status_code)

        raw_txins: List[dict] = json.loads(response.text)["unspent_outputs"]
        txins: List[TxIn] = []
        for raw_txin in raw_txins:
            txid = lx(raw_txin["tx_hash"])
            vout = raw_txin["tx_output_n"]
            txin = TxIn(raw_txin["value"], COutPoint(txid, vout))
            txins.append(txin)

        return txins
