import json

import requests
from bitcointx.core import CTransaction as Transaction

from errors.fee_estimation_api_error import FeeEstimationAPIError
from persistence.config import Network


class TxBroadcastClient:
    URL = "https://api.blockcypher.com/v1/btc/{network}/txs/push"

    class Network:
      MAINNET = "main"
      TESTNET = "test3"

    def __init__(self, app_network: str):
        if app_network == Network.MAINNET:
            self.network = self.Network.MAINNET
        elif app_network == Network.TESTNET:
            self.network = self.Network.TESTNET

    def broadcast_transaction(self, tx: Transaction):
        url = self.URL.format(network=self.network)
        response = requests.post(url, json.dumps({"tx": tx.serialize().hex()}))
        if response.status_code != 201:
            raise FeeEstimationAPIError(response.status_code)
        return True
