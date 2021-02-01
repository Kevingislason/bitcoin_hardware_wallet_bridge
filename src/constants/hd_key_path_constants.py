from bitcointx.core.key import BIP32Path


def bip_44_keypath():
    BIP_44_KEYPATH = "44'"
    return BIP32Path(BIP_44_KEYPATH)

def bip_49_keypath():
    BIP_49_KEYPATH = "49'"
    return BIP32Path(BIP_49_KEYPATH)

def bip_84_keypath():
    BIP_84_KEYPATH = "84'"
    return BIP32Path(BIP_84_KEYPATH)

def external_chain_keypath():
    EXTERNAL_CHAIN_KEYPATH = "0"
    return BIP32Path(EXTERNAL_CHAIN_KEYPATH)

def change_chain_keypath():
    CHANGE_CHAIN_KEYPATH = "1"
    return BIP32Path(CHANGE_CHAIN_KEYPATH)


BIP_KEYPATH_INDEX = 1
CHANGE_KEYPATH_INDEX = 3
CHILD_NUMBER_KEYPATH_INDEX = 4

# HD keys up to this index are derived on the hardware wallet,
# HD keys from this index are derived within the application
APP_BASE_KEYPATH_INDEX = CHANGE_KEYPATH_INDEX
