import bitcointx

from models.serial_connection_state import SerialConnectionState
from models.watch_only_wallet import WatchOnlyWallet
from networking.blockchain.blockchain_client_interface import (
    BlockchainClientInterface as BlockchainClient
)
from networking.blockchain.block_explorer_client import BlockExplorerClient
from networking.blockchain.node_client import NodeClient
from networking.serial.serial_client import SerialClient
from persistence.config import (
    NetworkClient, Config
)


class MainController():
    # App State
    watch_only_wallet: WatchOnlyWallet
    serial_connection_state: SerialConnectionState

    # Network clients
    blockchain_client: BlockchainClient
    serial_client: SerialClient

    def __init__(self, watch_only_wallet, serial_connection_state):
        self.watch_only_wallet = watch_only_wallet
        self.serial_connection = serial_connection_state

        self.serial_client = SerialClient()
        if Config.get_network_client() == NetworkClient.BLOCK_EXPLORER:
            self.blockchain_client = BlockExplorerClient()
        elif Config.get_network_client() == NetworkClient.BITCOIN_NODE:
            self.blockchain_client = NodeClient()

        # Tell bitcointx whether to use mainnet, testnet, or regtest
        bitcointx.select_chain_params(Config.get_chain_parameters())

    def send_transaction(self):
        self.watch_only_wallet.spendable_balance_satoshis = 999

        self.blockchain_client.get_txins(
            ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"])
