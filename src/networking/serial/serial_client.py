import os
from typing import Optional, List

from bitcointx.wallet import (
    CCoinExtPubKey as ExtPubKey,
    CCoinExtKey as ExtPrivKey,
    T_CCoinAddress as AddressType,
    P2PKHCoinAddress as P2PKHAddress,
    P2SHCoinAddress as P2SHAddress,
    P2WPKHCoinAddress as P2WPHKAddress
)

class SerialClient:
    #todo: make compatible w/ windows and Linux
    class USBPath:
        MAC = "/dev/tty.usbmodem3360376633382"


    def get_usb_path(self) -> str:
        return self.USBPath.MAC

    def is_connected(self) -> bool:
        usb_path = self.get_usb_path()
        return os.path.exists(usb_path)

    def authenticate(self) -> bool:
        return True

    # todo: derive wallet xpub
    def get_test_wallet_xpubs(self) -> List[ExtPubKey]:
        #testing only
        res = [
            (
                ExtPrivKey.from_seed(bytes([33 for _ in range(64)])).derive_path("m/49'/1'").neuter(),
                P2SHAddress
            )
        ]
        return res
        #
        # 44, 49, 84
        #[P2SHAddress, P2WPKHAddress, P2PKHAddress]:


    def get_master_fingerprint(self):
        return ExtPrivKey.from_seed(bytes([33 for _ in range(64)])).fingerprint


    def get_wallet_xpubs(self) -> List[ExtPubKey]:
        pass






    def get_address_type(self) -> Optional[AddressType]:
        return P2SHAddress
