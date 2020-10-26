import bitcointx
from bitcointx.core.serialize import Hash160
from bitcointx.core.script import CScript, OP_HASH160, OP_EQUAL
from bitcointx.wallet import (
    CPubKey as PubKey,
    CCoinExtPubKey as ExtPubKey,
    P2PKHCoinAddress as P2PKHAddress,
    P2SHCoinAddress as P2SHAddress,
    P2WPKHCoinAddress as P2WPKHAddress,
    T_CCoinAddress as AddressType,
    T_P2PKHCoinAddress as P2PKHAddressType,
    T_P2SHCoinAddress as P2SHAddressType,
    T_P2WPKHCoinAddress as P2WPKHAddressType
)

from bitcoin_types.wallet_address import WalletAddress
from bitcoin_types.block import Block
from constants.wallet_recovery_constants import CHANGE_GAP_LIMIT, EXTERNAL_GAP_LIMIT
from models.serial_connection_state import SerialConnectionState
from models.watch_only_wallet import WatchOnlyWallet
from networking.blockchain.blockchain_client_interface import (
    BlockchainClientInterface as BlockchainClient
)
from networking.blockchain.block_explorer_client import BlockExplorerClient
from networking.blockchain.node_client import NodeClient
from networking.serial.serial_client import SerialClient
from persistence.config import (
    BlockchainClient, Config
)
from persistence.wallet_file import WalletFile


class MainController():
    # App State
    watch_only_wallet: WatchOnlyWallet
    serial_connection_state: SerialConnectionState

    # Network clients
    blockchain_client: BlockchainClient
    serial_client: SerialClient

    def __init__(self, watch_only_wallet: WatchOnlyWallet,
                 serial_connection_state: SerialConnectionState):
        # Set up class
        self.watch_only_wallet = watch_only_wallet
        self.serial_connection = serial_connection_state
        self.serial_client = SerialClient()
        if Config.get_blockchain_client() == BlockchainClient.BLOCK_EXPLORER:
            self.blockchain_client = BlockExplorerClient()
        elif Config.get_blockchain_client() == BlockchainClient.BITCOIN_NODE:
            self.blockchain_client = NodeClient()

        # Tell bitcointx whether to use mainnet, testnet, or regtest
        bitcointx.select_chain_params(Config.get_chain_parameters())

        self.recover_wallet()

        if WalletFile.exists():
            self.watch_only_wallet.load(*WalletFile.load())
            self.watch_only_wallet.refresh_balances()
            self.sync_to_blockchain()

    # we want to see a spinner while this is happening
    # todo: validate addresses w/ balances first so we don't have to wait several minutes to spend
    def sync_to_blockchain(self):
        most_recent_block = self.blockchain_client.get_most_recent_block()
        if most_recent_block == self.watch_only_wallet.current_block:
            return

        while self.blockchain_client.block_is_orphan(self.watch_only_wallet.current_block):
            self.purge_orphaned_block(self.watch_only_wallet.current_block)

        for address in self.watch_only_wallet.addresses_iter():
                # todo: update wallet history
                # prev_tx_ins = address.tx_ins
                current_tx_ins = self.blockchain_client.get_tx_ins_by_address(address)
                # new_sent_tx_ins = list(set(prev_tx_ins) - set(current_tx_ins))
                address.tx_ins = current_tx_ins
                # new_received_tx_ins = list(set(current_tx_ins) - set(prev_tx_ins))

        self.watch_only_wallet.current_block = most_recent_block
        self.watch_only_wallet.refresh_balances()
        WalletFile.save(self.watch_only_wallet)


    def purge_orphaned_block(self, orphan: Block):
        #todo: purge history
        for address in self.watch_only_wallet.addresses_iter():
            if address.tx_ins:
                address.tx_ins = [
                    tx_in for tx_in in address.tx_ins if tx_in.block.hash != orphan.hash
                ]
                if not address.tx_ins:
                    address.is_fresh = self.blockchain_client.address_is_fresh(address)

        self.watch_only_wallet.current_block = self.blockchain_client.get_block_by_hash(
            self.watch_only_wallet.current_block.prev_hash
        )
        self.watch_only_wallet.refresh_balances()
        WalletFile.save(self.watch_only_wallet)


    def recover_wallet(self):
        # Get wallet data from the hardware wallet
        wallet_xpub = self.serial_client.get_wallet_xpub()

        # Discover external addresses (defaulting to P2WPKHAddress if seed is totally unused)
        for address_type in [P2PKHAddressType, P2SHAddressType, P2WPKHAddressType]:
            external_addresses = self.discover_addresses(wallet_xpub, address_type, False)
            if external_addresses:
                break

        # Discover change addresses
        change_addresses = self.discover_addresses(wallet_xpub, address_type, True)

        # Update wallet model
        self.watch_only_wallet.load(
            wallet_xpub,
            address_type,
            Block.genesis_block(),
            external_addresses,
            change_addresses
        )
        # Persist wallet data
        WalletFile(self.watch_only_wallet)

        self.sync_to_blockchain()


    def discover_addresses(self,
                           wallet_xpub: ExtPubKey,
                           address_type: AddressType,
                           is_change_chain: bool):

        gap_limit = CHANGE_GAP_LIMIT if is_change_chain else EXTERNAL_GAP_LIMIT
        current_gap = 0
        discovered_addresses = []

        while current_gap < gap_limit:
            address_index = len(discovered_addresses)
            child_address = WalletAddress(wallet_xpub, address_type, address_index, is_change_chain, was_recovered=True)

            if self.blockchain_client.address_is_fresh(child_address):
                child_address.is_fresh = False
                current_gap = 0
            else:
                current_gap += 1
            discovered_addresses.append(child_address)
        return discovered_addresses[:-gap_limit]


    def derive_change_address(self):
        new_address = WalletAddress(
            self.watch_only_wallet.master_xpub,
            self.watch_only_wallet.address_type,
            len(self.watch_only_wallet.change_addresses),
            True
        )
        self.watch_only_wallet.change_addresses[str(new_address)] = new_address
        WalletFile.save(self.watch_only_wallet)
        return new_address


    def derive_external_address(self, label):
        new_address = WalletAddress(
            self.watch_only_wallet.wallet_xpub,
            self.watch_only_wallet.address_type,
            len(self.watch_only_wallet.external_addresses),
            label=label
        )
        self.watch_only_wallet.external_addresses[str(new_address)] = new_address
        WalletFile.save(self.watch_only_wallet)
        return new_address
