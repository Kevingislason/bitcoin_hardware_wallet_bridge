from constants.unit_constants import (TESTNET_BITCOIN_UNITS,
                                      TESTNET_SATOSHIS_UNITS)
from persistence.config import BalanceUnits, Network


def get_currency_symbol(network: str, units: str):
    if network == Network.MAINNET:
        return units
    elif network == Network.TESTNET:
        if units == BalanceUnits.BTC:
            return TESTNET_BITCOIN_UNITS
        return TESTNET_SATOSHIS_UNITS
