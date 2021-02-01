

from unittest.mock import patch

import pytest

from controllers.main_controller import MainController
from models.watch_only_wallet import WatchOnlyWallet
from persistence.config import BlockchainClient, Config, Network
from persistence.wallet_file import WalletFile


@patch("persistence.wallet_file.WalletFile.PATH", new='src/tests/test_load_wallet.json')
@patch("persistence.config.Config.get_network", new=lambda: Network.TESTNET)
@patch("controllers.main_controller.MainController.sync_to_blockchain", new=lambda _: None)
def test_load_wallet():
    watch_only_wallet = WatchOnlyWallet()
    controller = MainController(watch_only_wallet)
    assert len(controller.watch_only_wallet.external_addresses) == 1
    assert len(controller.watch_only_wallet.change_addresses) == 0
    assert controller.watch_only_wallet.spendable_balance_satoshis == 100000
