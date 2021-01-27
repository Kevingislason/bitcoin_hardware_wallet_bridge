import json
from json import JSONDecodeError
import os
import serial
from serial import SerialException
from typing import Optional, List, Dict
from bitcointx.core import (
    CTransaction as Transaction,
    x
)
from bitcointx.wallet import (
    CCoinExtPubKey as ExtPubKey,
    CCoinExtKey as ExtPrivKey,
    T_CCoinAddress as AddressType,
    P2PKHCoinAddress as P2PKHAddress,
    P2SHCoinAddress as P2SHAddress,
    P2WPKHCoinAddress as P2WPHKAddress,
)
from bitcointx.core.psbt import (
    PartiallySignedTransaction,
)

from bitcoin_types.hd_key_path import HDKeyPath
from bitcoin_types.hardware_wallet_init_dto import HardwareWalletInitDTO
from constants.network_constants import HARDWARE_WALLET_MAINNET, HARDWARE_WALLET_TESTNET
from persistence.config import (
    ChainParameters, Config
)
from persistence.hardware_wallet_file import HardwareWalletFile
from persistence.init_wallet_file import InitWalletFile

class OutgoingMessageHeader:
    REQUEST_INIT_WALLET = "init wallet"
    REQUEST_LOAD_WALLET = "load wallet"
    REQUEST_SIGN_TRANSACTION = "sign transaction"
    REQUEST_SHOW_ADDRESS = "show address"


class IncomingMessageHeader:
    INIT_WALLET_SUCCESS = "init wallet success"
    LOAD_WALLET_SUCCESS = "load wallet success"
    SIGN_TRANSACTION_RESULT = "sign transaction result"


#todo: handle serial exception
class SerialClient:
    port: serial.Serial
    #todo: make compatible w/ Windows and Linux
    class USBPath:
        MAC = "/dev/tty.usbmodem3360376633382"

    BAUD_RATE = 1200

    def __init__(self):
        self.port = None

    @property
    def usb_path(self) -> str:
        return self.USBPath.MAC

    def await_serial_connection(self):
        while True:
            if os.path.exists(self.usb_path):
                self.port = serial.Serial(self.usb_path, self.BAUD_RATE)
                return

    @property
    def network(self):
        chain_params = Config.get_chain_parameters()
        if chain_params == ChainParameters.MAINNET:
            return HARDWARE_WALLET_MAINNET
        elif chain_params == ChainParameters.TESTNET:
            return HARDWARE_WALLET_TESTNET



    def request_init_hardware_wallet(self) -> HardwareWalletInitDTO:
        message = json.dumps(
        {"header": OutgoingMessageHeader.REQUEST_INIT_WALLET,
            "payload": {
                "network": self.network}
            }
        )
        self.port.write(bytes(message + "\n", encoding="utf8"))
        response = self._read_message(IncomingMessageHeader.INIT_WALLET_SUCCESS)
        payload = response["payload"]
        HardwareWalletFile(payload["recovery_phrase_length"])
        return HardwareWalletInitDTO(payload)


    def request_load_hardware_wallet(self, watch_only_wallet) -> bool:
        message = json.dumps(
            {
                "header": OutgoingMessageHeader.REQUEST_LOAD_WALLET,
                "payload": {
                    "wallet_xpub": watch_only_wallet.xpub.base58_prefix.hex()
                                   + watch_only_wallet.xpub.to_bytes().hex(),
                    "wallet_keypath": str(watch_only_wallet.base_keypath),
                    "network": self.network,
                    "recovery_phrase_length": HardwareWalletFile.get_recovery_phrase_length(),
                }
            }
        )
        self.port.write(bytes(message + "\n", encoding="utf8"))
        response = self._read_message(IncomingMessageHeader.LOAD_WALLET_SUCCESS)
        return True


    def request_sign_transaction(self, psbt: PartiallySignedTransaction) -> Transaction:
        if not self.port:
            self.port = serial.Serial(self.usb_path, self.BAUD_RATE)
        message = json.dumps(
            {"header": OutgoingMessageHeader.REQUEST_SIGN_TRANSACTION,
            "payload": {
                "psbt": psbt.serialize().hex()}
            }
        )
        self.port.write(bytes(message + "\n", encoding="utf8"))
        response = self._read_message(IncomingMessageHeader.SIGN_TRANSACTION_RESULT)
        payload = response["payload"]
        if not bool(payload["success"]):
            return None
        return Transaction.deserialize(x(payload["transaction"]))



    def request_show_address(self, key_path: HDKeyPath):
        if not self.port:
            return

        message = json.dumps(
            {"header": OutgoingMessageHeader.REQUEST_SHOW_ADDRESS,
            "payload": {
                "key_path": str(key_path)}
            }
        )
        self.port.write(bytes(message + "\n", encoding="utf8"))


    def _read_message(self, expected_header: str) -> str:
        line = ""
        while True:
            character = self.port.read().decode("utf-8")
            line += character
            # Hack: Ignore junk output from micropy
            # Todo: make custom firmware to disable
            if line == ">>>" or character == "\n":
                line = ""
            elif character == "}":
                try:
                    message = json.loads(line)
                    line = ""
                    if message["header"] == expected_header:
                        return message
                except JSONDecodeError as j:
                    continue
