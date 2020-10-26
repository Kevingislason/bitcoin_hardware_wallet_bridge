import os
from typing import Optional

from bitcointx.wallet import CCoinExtPubKey as ExtPubKey
from bitcointx.wallet import (
    CCoinExtKey as ExtPrivKey,
    T_CCoinAddress as AddressType,
    T_P2PKHCoinAddress as P2PKHAddressType,
    T_P2SHCoinAddress as P2SHAddressType,
    T_P2WPKHCoinAddress as P2WPHKAddressType
)

class SerialClient:
    def await_connection(self) -> bool:
        return True

    def authenticate(self) -> bool:
        return True

    def get_wallet_xpub(self):
        #testing only
        return ExtPrivKey.from_seed(bytes([33 for _ in range(64)])).neuter()

        # return ExtPubKey(
        # "xpub6EnV9K1LzPtRDXqqcDkBk99uCFneHiHR3DBQxXcbuWzQoUGLfJiHeF3uDW1JZH3ZG7mr4TuNtPbgLYwEibEkcDcnQkQksZi7jm3eY8PqKFv")



    def get_address_type(self) -> Optional[AddressType]:
        return P2WPHKAddressType
