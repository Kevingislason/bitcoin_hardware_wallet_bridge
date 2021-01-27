import json
import os

class HardwareWalletFile:
    PATH = "hardware_wallet.json"

    def __new__(cls, recovery_phrase_length):
      hardware_wallet_data = {
        "recovery_phrase_length": recovery_phrase_length
      }
      with open(cls.PATH, 'w') as hardware_wallet_file:
         json.dump(hardware_wallet_data, hardware_wallet_file, indent=4)

    @classmethod
    def exists(cls):
      return os.path.exists(cls.PATH)

    @classmethod
    def get_recovery_phrase_length(cls) -> int:
      with open(cls.PATH, "r") as hardware_wallet_file:
        hardware_wallet_json = json.load(hardware_wallet_file)
      return hardware_wallet_json["recovery_phrase_length"]
