import json
import os
from json import JSONDecodeError
from typing import List, Optional

import serial
from bitcointx.core import CTransaction as Transaction
from bitcointx.core import x
from bitcointx.core.psbt import PartiallySignedTransaction
from bitcointx.wallet import CCoinExtPubKey as ExtPubKey
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from serial import SerialException

from models.hardware_wallet_init_dto import HardwareWalletInitDTO
from models.hd_key_path import HDKeyPath
from constants.network_constants import (HARDWARE_WALLET_MAINNET,
                                         HARDWARE_WALLET_TESTNET)
from persistence.config import Config, Network
from persistence.hardware_wallet_file import HardwareWalletFile


class OutgoingMessageHeader:
    REQUEST_INIT_WALLET = "init wallet"
    REQUEST_LOAD_WALLET = "load wallet"
    REQUEST_SIGN_TRANSACTION = "sign transaction"
    REQUEST_SHOW_ADDRESS = "show address"


class IncomingMessageHeader:
    INIT_WALLET_SUCCESS = "init wallet success"
    LOAD_WALLET_SUCCESS = "load wallet success"
    SIGN_TRANSACTION_RESULT = "sign transaction result"



class SerialClient(QObject):
    port: serial.Serial
    connection = pyqtSignal(bool)

    BAUD_RATE = 1200


    class USBPath:
        MAC = "/dev/tty.usbmodem3360376633382"

    def __init__(self, network: str):
        super().__init__()
        self.port = None
        if network == Network.MAINNET:
            self.network = HARDWARE_WALLET_MAINNET
        elif network == Network.TESTNET:
            self.network = HARDWARE_WALLET_TESTNET


    @property
    def usb_path(self) -> str:
        #todo: make compatible w/ Windows and Linux
        return self.USBPath.MAC


    @property
    def is_connected(self):
        return os.path.exists(self.usb_path) and self.port is not None


    def connect(self):
        while True:
            if os.path.exists(self.usb_path):
                self.port = serial.Serial(self.usb_path, self.BAUD_RATE)
                self.connection.emit(True)
                return


    def disconnect(self):
        self.port = None
        self.conection.emit(False)


    def request_init_hardware_wallet(self) -> HardwareWalletInitDTO:
        message = json.dumps(
        {"header": OutgoingMessageHeader.REQUEST_INIT_WALLET,
            "payload": {
                "network": self.network}
            }
        )
        self.write_message(message)
        response = self._read_message(IncomingMessageHeader.INIT_WALLET_SUCCESS)
        payload = response["payload"]
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
                    "recovery_phrase_length": HardwareWalletFile.load_recovery_phrase_length(),
                }
            }
        )
        self.write_message(message)
        response = self.read_message(IncomingMessageHeader.LOAD_WALLET_SUCCESS)
        return True


    def request_sign_transaction(self, psbt: PartiallySignedTransaction) -> Transaction:
        message = json.dumps(
            {"header": OutgoingMessageHeader.REQUEST_SIGN_TRANSACTION,
            "payload": {
                "psbt": psbt.serialize().hex()}
            }
        )
        self.write_message(message)
        response = self.read_message(IncomingMessageHeader.SIGN_TRANSACTION_RESULT)
        payload = response["payload"]
        if not bool(payload["success"]):
            return None
        psbt = PartiallySignedTransaction.deserialize(x(payload["psbt"]))
        return psbt.extract_transaction()


    def request_show_address(self, key_path: HDKeyPath):
        message = json.dumps(
            {"header": OutgoingMessageHeader.REQUEST_SHOW_ADDRESS,
            "payload": {
                "key_path": str(key_path)}
            }
        )
        self.write_message(message)

    def write_message(self, message: str):
        try:
            self.port.write(bytes(message + "\n", encoding="utf8"))
        except SerialException:
            self.disconnect()

    def read_message(self, expected_header: str):
        try:
            return self._read_message(expected_header)
        except SerialException:
            self.disconnect()

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
