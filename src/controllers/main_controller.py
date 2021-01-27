from typing import List, Tuple, Optional
from time import sleep
from requests.exceptions import ConnectionError, HTTPError
from serial import SerialException
import threading

from PyQt5.QtCore import (QObject, QThread, pyqtSignal, pyqtSlot)

from bitcoin_coin_selection.selection_algorithms.select_coins import (
    select_coins as select_coins_algo
)
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from bitcoin_coin_selection.selection_types.input_coin import InputCoin
from bitcoin_coin_selection.selection_types.output_group import OutputGroup
import bitcointx
from bitcointx.core import (
    b2x,
    CTxOut as TxOut,
    CTransaction as Transaction
)
from bitcointx.core.key import KeyStore, BIP32Path
from bitcointx.core.psbt import (
    PartiallySignedTransaction,
    PSBT_KeyDerivationInfo
)
from bitcointx.core.serialize import Hash160
from bitcointx.core.script import CScript, OP_HASH160, OP_EQUAL
from bitcointx.wallet import (
    CCoinExtKey as ExtPrivKey,
    CPubKey as PubKey,
    CCoinAddress as ExternalAddress,
    CCoinExtPubKey as ExtPubKey,
    P2PKHCoinAddress as P2PKHAddress,
    P2SHCoinAddress as P2SHAddress,
    P2WPKHCoinAddress as P2WPKHAddress,
    T_CCoinAddress as AddressType,
    T_P2PKHCoinAddress as P2PKHAddressType,
    T_P2SHCoinAddress as P2SHAddressType,
    T_P2WPKHCoinAddress as P2WPKHAddressType
)

from bitcoin_types.utxo import Utxo
from bitcoin_types.wallet_address import WalletAddress
from bitcoin_types.block import Block
from bitcoin_types.hd_key_path import HDKeyPath
from constants.transaction_size_constants import TX_BASE_BYTES, P2PKH_OUTPUT_BYTES
from constants.wallet_recovery_constants import CHANGE_GAP_LIMIT, EXTERNAL_GAP_LIMIT
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
from persistence.init_wallet_file import InitWalletFile
from persistence.wallet_file import WalletFile
from utils.coin_selection_utils import (
    map_coin_selection_to_utxos,
    map_utxos_to_output_groups,
    get_total_effective_value
)


class MainController(QObject):
    # App State
    network_connection = pyqtSignal(bool)
    serial_connection = pyqtSignal(bool)
    watch_only_wallet: WatchOnlyWallet

    # Network clients
    blockchain_client: BlockchainClient
    serial_client: SerialClient

    def __init__(self, watch_only_wallet: WatchOnlyWallet):
        super().__init__()
        # Tell bitcointx whether to use mainnet, testnet, or regtest
        bitcointx.select_chain_params(Config.get_chain_parameters())
        self.watch_only_wallet = watch_only_wallet
        if Config.get_blockchain_client() == BlockchainClient.BLOCK_EXPLORER:
            self.blockchain_client = BlockExplorerClient()
        elif Config.get_blockchain_client() == BlockchainClient.BITCOIN_NODE:
            self.blockchain_client = NodeClient()
        self.serial_client = SerialClient()

        # Wallet is already set up
        if WalletFile.exists():
            self.watch_only_wallet.load(*WalletFile.load())
        # Wallet already got HD keys from the hardware wallet, but haven't
        # properly recovered balances on this side
        elif InitWalletFile.exists():
            self.recover_wallet(*InitWalletFile.load())




        # test only #
        # self.serial_client.request_load_hardware_wallet(self.watch_only_wallet)
        # address = ExternalAddress("mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB")
        # target_value = 10000
        # selection = self.select_coins(10000, address, False)
        # if selection.outcome == selection.Outcome.SUCCESS:
        #     selected_utxos = map_coin_selection_to_utxos(
        #         selection, self.watch_only_wallet)
        #     malicious_transaction = self.assemble_malicious_tx(
        #         address, selected_utxos, target_value, selection.change_value
        #     )
        #     transaction = self.assemble_tx(address, selected_utxos, target_value, selection.change_value)

        #     psbt = self.assemble_psbt(transaction, selected_utxos)
        #     self.serial_client.request_sign_transaction(psbt)


        # else:
        #     raise Exception("not enough money")
        # end test only #

    def sync_to_external_data(self):
        self.sync_to_blockchain_loop_async()
        self.sync_to_hardware_wallet_loop_async()



    def _sync_to_blockchain(self):
        try:
            most_recent_block = self.blockchain_client.get_most_recent_block()
            if most_recent_block == self.watch_only_wallet.current_block:
                self.network_connection.emit(True)
                return

            while self.blockchain_client.block_is_orphan(self.watch_only_wallet.current_block):
                self.purge_orphaned_block(self.watch_only_wallet.current_block)

            for address in self.watch_only_wallet.addresses:
                    # It's necessary to do a diff like this so as not to get rid of utxos that are
                    # e.g. pending spend or unconfirmed
                    prev_utxos = address.utxos
                    current_utxos = self.blockchain_client.get_utxos_by_address(address)
                    new_sent_utxos = [utxo for utxo in prev_utxos if utxo not in current_utxos]
                    new_received_utxos = [utxo for utxo in current_utxos if utxo not in prev_utxos]
                    address.utxos += new_received_utxos
                    address.utxos = [utxo for utxo in address.utxos if utxo not in new_sent_utxos]

            self.watch_only_wallet.current_block = most_recent_block
            self.watch_only_wallet.refresh_balances()
            WalletFile.save(self.watch_only_wallet)
            self.network_connection.emit(True)

        except ConnectionError:
            self.network_connection.emit(False)


    def _sync_to_blockchain_loop(self):
        bitcointx.select_chain_params(Config.get_chain_parameters())
        while True:
            if WalletFile.exists():
                self._sync_to_blockchain()
                sleep(5)


    def sync_to_blockchain_loop_async(self):
        self.thread = threading.Thread(target=self._sync_to_blockchain_loop)
        self.thread.start()


    def _sync_to_hardware_wallet_loop(self):
        while True:
            try:
                if not self.serial_client.port:
                    self.serial_client.await_serial_connection()
                    self.serial_connection.emit(True)
                    if InitWalletFile.exists():
                        self.serial_client.request_load_hardware_wallet(self.watch_only_wallet)
                    else:
                        init_hardware_wallet_data = self.serial_client.request_init_hardware_wallet()
                        InitWalletFile(init_hardware_wallet_data)
                        self.recover_wallet(*InitWalletFile.load())
            except SerialException:
                self.serial_client.port = None
                self.serial_connection.emit(False)

    def sync_to_hardware_wallet_loop_async(self):
        thread = threading.Thread(target=self._sync_to_hardware_wallet_loop)
        thread.start()


    def purge_orphaned_block(self, orphan: Block):
        for address in self.watch_only_wallet.addresses:
            if address.utxos:
                address.utxos = [
                    utxo for utxo in address.utxos if utxo.block.hash != orphan.hash
                ]
                if not address.utxos:
                    address.is_fresh = self.blockchain_client.address_is_fresh(address)

        self.watch_only_wallet.current_block = self.blockchain_client.get_block_by_hash(
            self.watch_only_wallet.current_block.prev_hash
        )
        self.watch_only_wallet.refresh_balances()
        WalletFile.save(self.watch_only_wallet)

    def recover_wallet(self, candidate_wallets: List[Tuple[ExtPubKey, HDKeyPath]], master_fingerprint: bytes):
        # Discover external addresses (defaulting to P2WPKHAddress if seed is totally unused)
        for wallet_xpub, base_keypath in candidate_wallets:
            external_addresses = self.discover_addresses(wallet_xpub, base_keypath, False)
            if external_addresses:
                break

        # Discover change addresses
        change_addresses = self.discover_addresses(wallet_xpub, base_keypath, True)

        # Update wallet model
        self.watch_only_wallet.load(
            wallet_xpub,
            master_fingerprint,
            base_keypath,
            Block.genesis_block(),
            external_addresses,
            change_addresses
        )

        # Persist wallet data
        WalletFile(self.watch_only_wallet)

        if not self.watch_only_wallet.change_addresses:
            self.derive_change_address()

    def discover_addresses(self,
                           wallet_xpub: ExtPubKey,
                           base_keypath: str,
                           is_change_chain: bool) -> List[WalletAddress]:

        gap_limit = CHANGE_GAP_LIMIT if is_change_chain else EXTERNAL_GAP_LIMIT
        current_gap = 0
        discovered_addresses = []

        while current_gap < gap_limit:
            address_index = len(discovered_addresses)
            child_address = WalletAddress(wallet_xpub, base_keypath, address_index,
                                          is_change_chain, was_recovered=True)

            if self.blockchain_client.address_is_fresh(child_address):
                child_address.is_fresh = False
                current_gap = 0
            else:
                current_gap += 1
            discovered_addresses.append(child_address)
        return discovered_addresses[:-gap_limit]


    def derive_change_address(self) -> WalletAddress:
        new_address = WalletAddress(
            self.watch_only_wallet.xpub,
            self.watch_only_wallet.base_keypath,
            len(self.watch_only_wallet.change_addresses),
            True
        )
        self.watch_only_wallet.change_addresses[str(new_address)] = new_address
        WalletFile.save(self.watch_only_wallet)
        return new_address


    def derive_external_address(self, label) -> WalletAddress:
        new_address = WalletAddress(
            self.watch_only_wallet.xpub,
            self.watch_only_wallet.base_keypath,
            len(self.watch_only_wallet.external_addresses),
            label=label
        )
        self.watch_only_wallet.external_addresses[str(new_address)] = new_address
        WalletFile.save(self.watch_only_wallet)
        return new_address


    def select_coins(self, target_value: int, recipient: ExternalAddress, is_priority: bool) -> CoinSelection:
        utxo_pool = map_utxos_to_output_groups(self.watch_only_wallet)
        # Get fees
        fees_per_byte = self.blockchain_client.get_current_fee_rate(is_priority)
        # Get tx size not including inputs (which we in any case don't know yet)
        not_input_size_in_bytes = Utxo.output_size(recipient) + TX_BASE_BYTES
        # Run complex coin selection algorithm to select coins that will minimize fees
        return select_coins_algo(utxo_pool,
                          target_value,
                          fees_per_byte,
                          fees_per_byte, #todo: figure out some way to guess at long term fees
                          Utxo.output_size(self.watch_only_wallet.addresses[0]),
                          Utxo.spend_size(self.watch_only_wallet.addresses[0]),
                          not_input_size_in_bytes
        )

    def get_max_possible_spend(self, is_priority: bool,
                      recipient: Optional[ExternalAddress]) -> int:

        # todo: single source of truth for fee rate
        fee_rate = self.blockchain_client.get_current_fee_rate(is_priority)
        total_effective_value = get_total_effective_value(self.watch_only_wallet, fee_rate)

        if recipient:
            output_size = Utxo.output_size(recipient)
        else:
            # assume largest possible output
            output_size = P2PKH_OUTPUT_BYTES

        not_input_bytes = TX_BASE_BYTES + output_size
        not_input_fees = not_input_bytes * fee_rate
        return max(total_effective_value - not_input_fees, 0)


    def assemble_tx(self, recipient: ExternalAddress, utxos: List[Utxo],
                    target_value: int, change_value: int) -> Transaction:
        tx_ins = [utxo.tx_in for utxo in utxos]
        tx_outs = []
        # 1 output for the "main" destination of the payment
        spend_tx_out = TxOut(target_value, recipient.to_scriptPubKey())
        tx_outs.append(spend_tx_out)
        # 1 output for change (if applicable)
        if change_value != 0:
            if self.watch_only_wallet.last_change_address.is_fresh:
                change_address = self.watch_only_wallet.last_change_address
                change_address.is_fresh = False
            else:
                change_address = self.derive_change_address()
            change_tx_out = TxOut(change_value, change_address.to_scriptPubKey())
            tx_outs.append(change_tx_out)

        return Transaction(tx_ins, tx_outs)


    # Assemble an unsigned transaction in Partially Signed Bitcoin Trnsaction Format
    # See https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki
    def assemble_psbt(self, transaction: Transaction, utxos: List[Utxo]) -> PartiallySignedTransaction:
        psbt = PartiallySignedTransaction(unsigned_tx=transaction)
        self._assembe_psbt_inputs(psbt, utxos)
        self._assemble_psbt_change_output(psbt)
        return psbt


    def _assembe_psbt_inputs(self, psbt: PartiallySignedTransaction, utxos: List[Utxo]):
        for i, psbt_input in enumerate(psbt.inputs):
            utxo = utxos[i]
            address = self.watch_only_wallet.get_address(utxo.address)
            address_derivation_info = PSBT_KeyDerivationInfo(
                self.watch_only_wallet.master_fingerprint, BIP32Path(address.key_path)
            )
            psbt_input.derivation_map[address.pub_key] = address_derivation_info

            if utxo.is_witness_utxo:
                psbt_input.set_utxo(utxo.tx_out, psbt.unsigned_tx)
            else:
                transaction = self.blockchain_client.get_transaction(utxo.tx_hash)
                psbt_input.set_utxo(transaction, psbt.unsigned_tx)


    def _assemble_psbt_change_output(self, psbt: PartiallySignedTransaction):
        if len(psbt.outputs) == 2:
            change_output = psbt.outputs[1]

            address_derivation_info = PSBT_KeyDerivationInfo(
                self.watch_only_wallet.master_fingerprint,
                BIP32Path(self.watch_only_wallet.last_change_address.key_path)
            )
            change_output.derivation_map[last_change_address.pub_key] = address_derivation_info


    def sign_psbt(self, psbt: PartiallySignedTransaction):
        # lines 418 - 430 in test_psbt should get you there

        xpriv = ExtPrivKey("tprv8ZgxMBicQKsPehjZHpLLc55zCdP2KmM5afjfn48zmJcJAU4Jv9BcKunh8Ad5V8iHEo2juZRchVkXrRNnqq7cdNpiRsH784hzp1SWwVY7bNP")

        kstore = KeyStore(xpriv, require_path_templates=False)

        result = psbt.sign(kstore, finalize=True)

        print(b2x(psbt.extract_transaction().serialize()))

        return result.is_final and result.is_ready



    def request_hardware_wallet_display_address(self, key_path: HDKeyPath):
        self.serial_client.request_show_address(key_path)


    def broadcast_signed_transaction(self, transaction: Transaction) -> Optional[str]:
        tx_url = self.blockchain_client.broadcast_signed_transaction(transaction)
        if tx_url:
            # Need to save immediately so we don't forget that the last change address will be used
            WalletFile.save(self.watch_only_wallet)
        return tx_url


    def cancel_transaction(self):
        self.watch_only_wallet.last_change_address.is_fresh = True







