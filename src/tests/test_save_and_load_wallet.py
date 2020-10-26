

import pytest
from unittest.mock import patch

from persistence.config import ChainParameters, Config, BlockchainClient
from persistence.wallet_file import WalletFile

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from models.serial_connection_state import SerialConnectionState


@patch("persistence.wallet_file.WalletFile.PATH", new='src/tests/test_load_wallet.json')
@patch("persistence.config.Config.get_chain_parameters", new=lambda: ChainParameters.TESTNET)
@patch("persistence.config.Config.get_blockchain_client", new=lambda: BlockchainClient.BLOCK_EXPLORER)
@patch("controllers.main_controller.MainController.sync_to_blockchain", new=lambda _: None)
def test_load_wallet():
    watch_only_wallet = WatchOnlyWallet()
    serial_connection_state = SerialConnectionState()
    controller = MainController(watch_only_wallet, serial_connection_state)
    assert len(controller.watch_only_wallet.external_addresses) == 1
    assert len(controller.watch_only_wallet.change_addresses) == 0
    assert controller.watch_only_wallet.spendable_balance_satoshis == 100000


