import json
from typing import List, Optional, Tuple, Union

import requests
from bitcointx.core import CMutableTxIn as TxIn
from bitcointx.core import CMutableTxOut as TxOut
from bitcointx.core import COutPoint as OutPoint
from bitcointx.core import CTransaction as Transaction
from bitcointx.core import lx, x
from bitcointx.wallet import CCoinAddress as Address
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from requests.exceptions import ConnectionError

from models.block import Block
from models.utxo import Utxo
from constants.money_constants import SATOSHIS_PER_COIN
from errors.blockchain_api_error import BlockchainAPIError
from persistence.config import Config, Network


class BlockchainClient(QObject):
    URL = "https://sochain.com/api/v2/{query}/{network}/{param}"

    class Query:
        TX = "tx"
        GET_TX = "get_tx"
        GET_UNSPENT_TX = "get_tx_unspent"
        GET_RECEIVED_TX = "get_tx_received"
        GET_NETWORK_INFO = "get_info"
        GET_BLOCK = "get_block"

    class Network:
        MAINNET = "BTC"
        TESTNET = "BTCTEST"

    network: str
    connection = pyqtSignal(bool)

    def __init__(self, app_network: str):
        super().__init__()
        if app_network == Network.MAINNET:
            self.network = self.Network.MAINNET
        elif app_network == Network.TESTNET:
            self.network = self.Network.TESTNET

    def get_most_recent_block(self) -> Block:
        network_info = self.query_api(self.Query.GET_NETWORK_INFO)
        current_block_number = network_info["blocks"]
        current_block = self.query_api(self.Query.GET_BLOCK, current_block_number)
        current_block_hash = current_block["blockhash"]
        prev_block_hash = current_block["previous_blockhash"]
        return Block(current_block_hash, current_block_number, prev_block_hash)


    def get_block_by_hash(self, block_hash: str) -> Block:
        block = self.query_api(self.Query.GET_BLOCK, block_hash)
        block_number = block["block_no"]
        prev_block_hash = block["previous_blockhash"]
        return Block(block_hash, block_number, prev_block_hash)


    def get_block_by_tx(self, tx_hash: str) -> Block:
        tx_data = self.query_api(self.Query.TX, tx_hash)
        block_number = tx_data["block_no"]
        block_hash = tx_data["blockhash"]
        return Block(block_hash, block_number)


    def get_transaction(self, tx_hash: str) -> Transaction:
        tx_data = self.query_api(self.Query.GET_TX, tx_hash)
        tx_hex = tx_data["tx_hex"]
        return Transaction.deserialize(x(tx_hex))


    def block_is_orphan(self, block: Block) -> bool:
        return self.query_api(self.Query.GET_BLOCK, block.hash)["is_orphan"]


    def address_is_fresh(self, address: Address) -> bool:
        received_payments = self.query_api(self.Query.GET_RECEIVED_TX, str(address))["txs"]
        return len(received_payments) > 0


    def get_utxos_by_address(self, address: Address) -> List[Utxo]:
        raw_utxos = self.query_api(self.Query.GET_UNSPENT_TX, str(address))["txs"]
        utxos: List[Utxo] = []

        for raw_utxo in raw_utxos:
            value = int(float(raw_utxo["value"]) * SATOSHIS_PER_COIN)
            tx_hash = raw_utxo["txid"]
            block = self.get_block_by_tx(tx_hash)
            vout = raw_utxo["output_no"]

            tx_in = TxIn(OutPoint(lx(tx_hash), vout))
            tx_out = TxOut(value, address.to_scriptPubKey())

            utxo = Utxo(block, tx_in, tx_out)
            utxos.append(utxo)

        return utxos

    def query_api(self, query: str, param: Optional[Union[str, int]] = None):
        try:
            response = requests.get(
                self.URL.format(
                    query=query,
                    network=self.network,
                    param=param if param else "",
                )
            )
        except ConnectionError as e:
            self.connection.emit(False)
            raise e
        if response.status_code != 200:
            raise BlockchainAPIError(response.status_code)
        self.connection.emit(True)
        return json.loads(response.text)["data"]
