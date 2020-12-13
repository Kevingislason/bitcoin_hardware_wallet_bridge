import json
import requests
from typing import List, Optional, Tuple, Union

from bitcointx.core import (
    COutPoint as OutPoint,
    CMutableTxIn as TxIn,
    CMutableTxOut as TxOut,
    lx
)
from bitcointx.wallet import (
    CCoinAddress as Address,
)

from bitcoin_types.block import Block
from bitcoin_types.utxo import Utxo
from constants.money_constants import SATOSHIS_PER_COIN
from persistence.config import Config, ChainParameters
from errors.block_explorer_api_error import BlockExplorerAPIError
from networking.blockchain.blockchain_client_interface import BlockchainClientInterface


class BlockExplorerClient(BlockchainClientInterface):
    URL = "https://sochain.com/api/v2/{query}/{network}/{param}"
    FEE_URL = "https://api.blockchain.info/mempool/fees"

    class Query:
        TX = "tx"
        GET_UNSPENT_TX = "get_tx_unspent"
        GET_RECEIVED_TX = "get_tx_received"
        GET_NETWORK_INFO = "get_info"
        GET_BLOCK = "get_block"

    class Network:
        MAINNET = "BTC"
        TESTNET = "BTCTEST"

    network: str

    def __init__(self):
        super().__init__()
        chain_parameters = Config.get_chain_parameters()
        if chain_parameters == ChainParameters.MAINNET:
            self.network = self.Network.MAINNET
        elif chain_parameters == ChainParameters.TESTNET:
            self.network = self.Network.TESTNET


    def get_current_fee_rate(self, is_priority: bool):
        response = requests.get(self.FEE_URL)
        if response.status_code != 200 and response.status_code != 404:
            raise BlockExplorerAPIError(response.status_code)
        if is_priority:
            return json.loads(response.text)["priority"]
        else:
            return json.loads(response.text)["regular"]


    def get_most_recent_block(self) -> Block:
        network_info = self.query_api(self.Query.GET_NETWORK_INFO)
        current_block_number = network_info["blocks"]
        current_block = self.query_api(self.Query.GET_BLOCK, current_block_number)
        current_block_hash = current_block["blockhash"]
        prev_block_hash = current_block["previous_blockhash"]
        return Block(current_block_hash, current_block_number, prev_block_hash)


    def get_block_by_number(self, block_number: int) -> Optional[Block]:
        block = self.query_api(self.Query.GET_BLOCK, block_number)
        block_hash = block.get("blockhash")
        if block_hash:
            prev_block_hash = block["previous_blockhash"]
            return Block(block_hash, block_number, prev_block_hash)
        return None


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
        response = requests.get(
            self.URL.format(
                query=query,
                network=self.network,
                param=param if param else "",
            )
        )
        if response.status_code != 200 and response.status_code != 404:
            raise BlockExplorerAPIError(response.status_code)

        return json.loads(response.text)["data"]


