from network.network_client_interface import NetworkClientInterface
from network.block_explorer_client import BlockExplorerClient
import configparser
from utils.config import config
# from bitcointx.core.key import


class PSBTBuilder():

    network_client: NetworkClientInterface
    master_extended_public_key =

    def __init__(self):

        if config.get() == BlockExplorerClient.NETWORK_CLIENT_TYPE:
            self.network_client = BlockExplorerClient()

        bitcointx.select_chain_params(NAME)

        utxos =
