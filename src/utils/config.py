from enum import Enum
from typing import Any
import configparser


class Config:
    CONFIG_FILE_PATH = "config.ini"

    class Field(Enum):
        NETWORK_CLIENT = "Network client"
        CHAIN_PARAMETERS = "Chain parameters"

    class NetworkClientSetting(Enum):
        BLOCK_EXPLORER = "Block explorer"
        BITCOIN_NODE = "Bitcoin node"

    # Required by python-bitcointx, see
    # https://github.com/Simplexum/python-bitcointx#selecting-the-chain-to-use
    class ChainParameterSetting(Enum):
        REGTEST = 'bitcoin/regtest'
        TESTNET = 'bitcoin/testnet'
        MAINNET = 'bitcoin'

    @staticmethod
    def get(field: Field) -> Any:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return config[field]

    @staticmethod
    def set(field: Field, value: Any):
        config = configparser.ConfigParser()
        config[key] = value
        with open(CONFIG_FILE_PATH, "w+") as configfile:
            config.write(configfile)
        configfile.close()

    @classmethod
    def get_network_client(cls) -> NetworkClient:
        cls.get(cls.Fields.NetworkClient)

    @classmethod
    def set_network_client(cls, network_client: NetworkClient):
        cls.set(cls.Field.NETWORK_CLIENT, network_client)

    @classmethod
    def get_chain_parameters(cls) -> ChainParameters:
        cls.get(cls.Fields.NetworkClient)

    @classmethod
    def set_network_client(cls, chain_parameters: ChainParameters):
        cls.set(cls.Field.CHAIN_PARAMETERS, chain_parameters)
