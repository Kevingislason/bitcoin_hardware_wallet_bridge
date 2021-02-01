from bitcointx.core.key import BIP32Path


class HDKeyPath(BIP32Path):
    def __eq__(self, other):
        return str(self) == str(other)
