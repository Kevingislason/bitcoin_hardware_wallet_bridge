BIP_44_KEYPATH = "m/44'/"
BIP_49_KEYPATH = "m/49'/"
BIP_84_KEYPATH = "m/84'/"

MAINNET_KEYPATH = "0'/"
TESTNET_KEYPATH = "1'/"

FIRST_ACCOUNT_KEYPATH = "0'/"

EXTERNAL_CHAIN_KEYPATH = "0/"
CHANGE_CHAIN_KEYPATH = "1/"


CHANGE_KEYPATH_INDEX = 3
CHILD_NUMBER_KEYPATH_INDEX = 4
# HD keys up to this index are derived on the hardware wallet,
# HD keys from this index are derived within the application
APP_BASE_KEYPATH_INDEX = CHANGE_KEYPATH_INDEX
