import pytest
from unittest.mock import patch, Mock

from persistence.config import ChainParameters, Config, BlockchainClient
from persistence.wallet_file import WalletFile

from bitcoin_types.block import Block
from controllers.main_controller import MainController
from networking.blockchain.block_explorer_client import BlockExplorerClient
from models.watch_only_wallet import WatchOnlyWallet
from models.serial_connection_state import SerialConnectionState


BLOCK_1_HEIGHT = 1863403
BLOCK_2_HEIGHT = 1863404
BLOCK_3_HEIGHT = 1863405
BLOCK_4_HEIGHT = 1863406

VALID_BLOCK_4_HASH = "0000000000000025ba8a3917184a70dcf39c30a94fc1f3e5d59d89024a694327"
VALID_BLOCK_3_HASH = "000000000000000128a3f663e278397f7c0652e945f779551cb7a30d3c921511"
VALID_BLOCK_2_HASH = "00000000000000a1b7423b7f5acd720dee6875a242d9f376a3c7d3eadb06a237"
VALID_BLOCK_1_HASH = "000000000000009eef6ebb9fe7a90b8e41673f34866121bbe5039d659d294b3b"

ORPHANED_BLOCK_3_HASH = "00000000000000ef46962afbc2bebc0f871b1e538c4936bc30d8497e0f1efb16"

# A block that will orphan the block we load from file
valid_block_4 = Block(
  VALID_BLOCK_4_HASH,
  BLOCK_4_HEIGHT,
  VALID_BLOCK_3_HASH
)
# The most recent non-orphaned block on in our wallet's chain
valid_block_2 = Block(
  VALID_BLOCK_2_HASH,
  BLOCK_2_HEIGHT,
  VALID_BLOCK_1_HASH
)

@patch("persistence.config.Config.PATH", new="src/tests/test_config.ini")
def setup_client():
  mock_client = BlockExplorerClient
  mock_client.get_block_by_hash =  Mock(return_value=valid_block_2)
  mock_client.get_most_recent_block = Mock(return_value=valid_block_4)
  mock_client.address_is_fresh = Mock(return_value=True)

  mock_client.block_is_orphan = lambda _, block: True if block.hash == ORPHANED_BLOCK_3_HASH else False
  mock_client.get_tx_ins_by_address = lambda _, address: address.tx_ins

# Replace the block explorer with a mock to simulate an orphaned block situation
@patch("networking.blockchain.block_explorer_client.BlockExplorerClient", new=setup_client())
# Mock out config stuff
@patch("persistence.config.Config.PATH", new="src/tests/test_config.ini")
@patch("persistence.wallet_file.WalletFile.PATH", new='src/tests/test_purge_block_wallet.json')
@patch("persistence.wallet_file.WalletFile.save", new=lambda _: None)
def test_purge_block():
    watch_only_wallet = WatchOnlyWallet()
    serial_connection_state = SerialConnectionState()
    controller = MainController(watch_only_wallet, serial_connection_state)
    # Tx_ins from the orphaned block should not show up in our balance
    assert watch_only_wallet.spendable_balance_satoshis == 0
    assert watch_only_wallet.unspendable_balance_satoshis == 888
    # Current block should be the most recent valid block
    assert watch_only_wallet.current_block == valid_block_4
    # Addresses that received a tx_in in an orphaned block should count as fresh
    assert list(watch_only_wallet.external_addresses.values())[0].is_fresh









