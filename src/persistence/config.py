import configparser
from os import path
from typing import Any


class Field:
    NETWORK_CLIENT = "Network client"
    CHAIN_PARAMETERS = "Chain parameters"
    BALANCE_UNITS = "Balance units"


class NetworkClient:
    BLOCK_EXPLORER = "Block explorer"
    BITCOIN_NODE = "Bitcoin node"


# Required by python-bitcointx, see
# https://github.com/Simplexum/python-bitcointx#selecting-the-chain-to-use
class ChainParameters:
    REGTEST = "bitcoin/regtest"
    TESTNET = "bitcoin/testnet"
    MAINNET = "bitcoin"


class BalanceUnits:
    SATOSHIS = "Satoshis"
    BTC = "BTC"


class Config:
    PATH = "config.ini"

    @classmethod
    def exists(cls):
        return path.exists(cls.PATH)

    @classmethod
    def set_defaults(cls):
        config = configparser.ConfigParser()
        config.add_section("Config")
        # config.add_section(Field.CHAIN_PARAMETERS)
        # config.add_section(Field.NETWORK_CLIENT)

        config.set("Config", str(Field.BALANCE_UNITS), str(BalanceUnits.BTC))
        config.set("Config", str(Field.CHAIN_PARAMETERS),
                   str(ChainParameters.MAINNET))
        config.set("Config", str(Field.NETWORK_CLIENT),
                   str(NetworkClient.BLOCK_EXPLORER))

        with open(cls.PATH, 'w+') as configfile:
            config.write(configfile)

    @classmethod
    def get(cls, field: Field) -> Any:
        config = configparser.ConfigParser()
        config.read(cls.PATH)
        return config["Config"][field]

    @classmethod
    def set(cls, field: Field, value: Any):
        config = configparser.ConfigParser()
        config[field] = value
        with open(cls.PATH, "w+") as configfile:
            config.write(configfile)
        configfile.close()

    @classmethod
    def get_network_client(cls) -> NetworkClient:
        return cls.get(Field.NETWORK_CLIENT)

    @classmethod
    def set_network_client(cls, network_client: NetworkClient):
        cls.set(Field.NETWORK_CLIENT, network_client)

    @classmethod
    def get_chain_parameters(cls) -> ChainParameters:
        return cls.get(Field.CHAIN_PARAMETERS)

    @classmethod
    def set_chain_parameters(cls, chain_parameters: ChainParameters):
        cls.set(Field.CHAIN_PARAMETERS, chain_parameters)

    @classmethod
    def get_balance_units(cls) -> BalanceUnits:
        return cls.get(Field.BALANCE_UNITS)

    @classmethod
    def set_balance_units(cls, balance_display_units: BalanceUnits):
        cls.set(Field.BALANCE_UNITS, balance_display_units)
