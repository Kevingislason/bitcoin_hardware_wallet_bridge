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

def mainnet_keypath():
    MAINNET_KEYPATH = "0'"
    return BIP32Path(MAINNET_KEYPATH)

def testnet_keypath():
    TESTNET_KEYPATH = "1'"
    return BIP32Path(TESTNET_KEYPATH)

def first_account_keypath():
    FIRST_ACCOUNT_KEYPATH = "0'"
    return BIP32Path(FIRST_ACCOUNT_KEYPATH)

def external_chain_keypath():
    EXTERNAL_CHAIN_KEYPATH = "0"
    return BIP32Path(EXTERNAL_CHAIN_KEYPATH)

def change_chain_keypath():
    CHANGE_CHAIN_KEYPATH = "1"
    return BIP32Path(CHANGE_CHAIN_KEYPATH)

def paths_are_equal(path1: BIP32Path, path2: BIP32Path):
    return str(path1) == str(path2)

BIP_KEYPATH_INDEX = 1
CHANGE_KEYPATH_INDEX = 3
CHILD_NUMBER_KEYPATH_INDEX = 4

# HD keys up to this index are derived on the hardware wallet,
# HD keys from this index are derived within the application
APP_BASE_KEYPATH_INDEX = CHANGE_KEYPATH_INDEX
