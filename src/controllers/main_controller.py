import threading
from time import sleep
from typing import List, Optional, Tuple

import bitcointx
from bitcointx import base58
from bitcointx.core import CTransaction as Transaction
from bitcointx.core import CTxOut as TxOut
from bitcointx.core import b2x
from bitcointx.core.key import BIP32Path
from bitcointx.core.psbt import (PartiallySignedTransaction,
                                 PSBT_KeyDerivationInfo)
from bitcointx.core.script import OP_EQUAL, OP_HASH160, CScript
from bitcointx.core.serialize import Hash160
from bitcointx.wallet import CCoinAddress as ExternalAddress
from bitcointx.wallet import CCoinExtPubKey as ExtPubKey
from bitcointx.wallet import CPubKey as PubKey
from bitcointx.wallet import P2PKHCoinAddress as P2PKHAddress
from bitcointx.wallet import P2SHCoinAddress as P2SHAddress
from bitcointx.wallet import P2WPKHCoinAddress as P2WPKHAddress
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from requests.exceptions import ConnectionError
from serial import SerialException

from bitcoin_coin_selection.selection_algorithms.select_coins import \
    select_coins as select_coins_algo
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection
from bitcoin_coin_selection.selection_types.coin_selection_params import \
    CoinSelectionParams
from bitcoin_coin_selection.selection_types.input_coin import InputCoin
from bitcoin_coin_selection.selection_types.output_group import OutputGroup
from models.block import Block
from models.hd_key_path import HDKeyPath
from models.utxo import Utxo
from models.wallet_address import WalletAddress
from constants.transaction_size_constants import (P2PKH_OUTPUT_BYTES,
                                                  TX_BASE_BYTES)
from constants.wallet_recovery_constants import (CHANGE_GAP_LIMIT,
                                                 EXTERNAL_GAP_LIMIT)
from models.watch_only_wallet import WatchOnlyWallet
from networking.blockchain.blockchain_client import BlockchainClient
from networking.blockchain.fee_estimation_client import FeeEstimationClient
from networking.blockchain.tx_broadcast_client import TxBroadcastClient
from networking.serial.serial_client import SerialClient
from persistence.config import Config
from persistence.hardware_wallet_file import HardwareWalletFile
from persistence.wallet_file import WalletFile
from utils.coin_selection_utils import (get_total_effective_value,
                                        map_coin_selection_to_utxos,
                                        map_utxos_to_output_groups)


class MainController(QObject):
    # App State
    watch_only_wallet: WatchOnlyWallet
    hardware_wallet_initialized = pyqtSignal()
    hardware_wallet_loaded = pyqtSignal()
    watch_only_wallet_initialized = pyqtSignal()

    # Network clients
    blockchain_client: BlockchainClient
    fee_estimation_client: FeeEstimationClient
    tx_broadcast_client: TxBroadcastClient
    serial_client: SerialClient

    def __init__(self, watch_only_wallet: WatchOnlyWallet):
        super().__init__()
        self.network = Config.get_network()
        bitcointx.select_chain_params(self.network)

        self.watch_only_wallet = watch_only_wallet
        self.blockchain_client = BlockchainClient(self.network)
        self.fee_estimation_client = FeeEstimationClient()
        self.tx_broadcast_client = TxBroadcastClient(self.network)
        self.serial_client = SerialClient(self.network)

        # Wallet is already set up
        if WalletFile.exists():
            self.watch_only_wallet.load(*WalletFile.load())
        # Wallet already got HD keys from the hardware wallet, but haven't
        # properly recovered balances on this side
        elif HardwareWalletFile.exists():
            self.recover_wallet(
                HardwareWalletFile.load_candidate_wallets(),
                HardwareWalletFile.load_master_fingerprint()
            )


    def _sync_to_blockchain(self):
        most_recent_block = self.blockchain_client.get_most_recent_block()
        if most_recent_block == self.watch_only_wallet.current_block:
            return

        while self.blockchain_client.block_is_orphan(self.watch_only_wallet.current_block):
            self.purge_orphaned_block(self.watch_only_wallet.current_block)

        for address in self.watch_only_wallet.addresses:
            self.update_address_utxos(address)


        self.watch_only_wallet.current_block = most_recent_block
        self.watch_only_wallet.refresh_balances()
        WalletFile.save(self.watch_only_wallet)


    def _sync_to_blockchain_loop(self):
        bitcointx.select_chain_params(self.network)
        while True:
            try:
                if WalletFile.exists():
                    self._sync_to_blockchain()
                    sleep(5)
            except ConnectionError:
                pass


    def sync_to_blockchain_loop_async(self):
        thread = threading.Thread(target=self._sync_to_blockchain_loop)
        thread.daemon = True
        thread.start()

    def _sync_to_hardware_wallet(self):
        if not self.serial_client.is_connected:
            self.serial_client.connect()
            if HardwareWalletFile.exists():
                self.serial_client.request_load_hardware_wallet(self.watch_only_wallet)
                self.hardware_wallet_loaded.emit()
            else:
                init_hardware_wallet_data = self.serial_client.request_init_hardware_wallet()
                HardwareWalletFile(init_hardware_wallet_data)
                self.hardware_wallet_initialized.emit()
                self.recover_wallet(
                    HardwareWalletFile.load_candidate_wallets(),
                    HardwareWalletFile.load_master_fingerprint()
                )

    def _sync_to_hardware_wallet_loop(self):
        bitcointx.select_chain_params(self.network)
        while True:
            try:
                self._sync_to_hardware_wallet()
            except SerialException:
                pass


    def sync_to_hardware_wallet_loop_async(self):
        thread = threading.Thread(target=self._sync_to_hardware_wallet_loop)
        thread.daemon = True
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

    def update_address_utxos(self, address: WalletAddress):
        # It's necessary to do a diff like this so as not to get rid of utxos
        # that are e.g. pending spend or unconfirmed
        prev_utxos = address.utxos
        current_utxos = self.blockchain_client.get_utxos_by_address(address)
        new_sent_utxos = [utxo for utxo in prev_utxos if utxo not in current_utxos]
        new_received_utxos = [utxo for utxo in current_utxos if utxo not in prev_utxos]
        address.utxos += new_received_utxos
        address.utxos = [utxo for utxo in address.utxos if utxo not in new_sent_utxos]


    def recover_wallet(
        self,
        candidate_wallets: List[Tuple[ExtPubKey, HDKeyPath]],
        master_fingerprint: bytes
    ):
        for wallet_xpub, base_keypath in candidate_wallets:
            external_addresses = self.discover_addresses(wallet_xpub, base_keypath, False)
            if external_addresses:
                break

        change_addresses = self.discover_addresses(wallet_xpub, base_keypath, True)

        self.watch_only_wallet.load(
            wallet_xpub,
            master_fingerprint,
            base_keypath,
            Block.genesis_block(),
            external_addresses,
            change_addresses
        )
        WalletFile(self.watch_only_wallet)
        self.watch_only_wallet_initialized.emit()

        if not self.watch_only_wallet.change_addresses:
            self.derive_change_address()

    def discover_addresses(
        self,
        wallet_xpub: ExtPubKey,
        base_keypath: str,
        is_change_chain: bool
    ) -> List[WalletAddress]:

        gap_limit = CHANGE_GAP_LIMIT if is_change_chain else EXTERNAL_GAP_LIMIT
        current_gap = 0
        discovered_addresses = []

        while current_gap < gap_limit:
            address_index = len(discovered_addresses)
            address = WalletAddress(
                wallet_xpub,
                base_keypath,
                address_index,
                is_change_chain,
                was_recovered=True
            )
            if self.blockchain_client.address_is_fresh(address):
                address.is_fresh = False
                current_gap = 0
            else:
                current_gap += 1
            discovered_addresses.append(address)
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

    def request_hardware_wallet_display_address(self, key_path: HDKeyPath):
        if self.serial_client.is_connected:
            self.serial_client.request_show_address(key_path)


    def select_coins(self, target_value: int, recipient: ExternalAddress, is_priority: bool) -> CoinSelection:
        output_groups = map_utxos_to_output_groups(self.watch_only_wallet)
        fees_per_byte = self.fee_estimation_client.get_current_fee_per_byte(is_priority)
        # Get tx size not including inputs (which we in any case don't know yet)
        not_input_size_in_bytes = Utxo.output_size(recipient) + TX_BASE_BYTES
        return select_coins_algo(
            CoinSelectionParams(
                output_groups,
                target_value,
                fees_per_byte,
                fees_per_byte,
                Utxo.output_size(self.watch_only_wallet.addresses[0]),
                Utxo.spend_size(self.watch_only_wallet.addresses[0]),
                not_input_size_in_bytes
            )
        )


    def get_max_possible_spend(self, is_priority: bool,
                      recipient: Optional[ExternalAddress]) -> int:
        fee_per_byte = self.blockchain_client.fee_estimation_client(is_priority)
        total_effective_value = get_total_effective_value(self.watch_only_wallet, fee_per_byte)

        if recipient:
            output_size = Utxo.output_size(recipient)
        else:
            # assume largest possible output
            output_size = P2PKH_OUTPUT_BYTES

        not_input_bytes = TX_BASE_BYTES + output_size
        not_input_fees = not_input_bytes * fee_per_byte
        return max(total_effective_value - not_input_fees, 0)


    def orchestrate_spend(self, address: ExternalAddress, selection: CoinSelection) -> str:
        tx = self.assemble_transaction(address, selection)
        psbt = self.assemble_psbt(tx, selection)
        signed_tx = self.serial_client.request_sign_transaction(psbt)
        if not signed_tx:
            return False
        self.tx_broadcast_client.broadcast_transaction(signed_tx)
        self.persist_spend(selection)
        return base58.encode(tx.GetTxid())


    def persist_spend(self, selection: CoinSelection):
        for utxo in map_coin_selection_to_utxos(selection, self.watch_only_wallet):
            utxo.is_awaiting_spend = True
        if selection.change_value > 0:
            self.watch_only_wallet.last_change_address.is_fresh = False
        WalletFile.save(self.watch_only_wallet)


    def assemble_transaction(
        self,
        recipient: ExternalAddress,
        selection: CoinSelection,
    ) -> Transaction:
        tx_ins = self.assemble_transaction_inputs(selection)
        tx_outs = self.assemble_transaction_outputs(recipient)
        return Transaction(tx_ins, tx_outs)


    def assemble_transaction_inputs(self, selection: CoinSelection):
        utxos = map_coin_selection_to_utxos(selection, self.watch_only_wallet)
        return [utxo.tx_in for utxo in utxos]

    def assemble_transaction_outputs(
        self,
        recipient:ExternalAddress,
        selection: CoinSelection
    ):
        spend_output = self.assemble_transaction_spend_output(recipient, selection)
        outputs = [spend_output]
        if selection.change_value != 0:
            change_output = self.assemble_transaction_change_output(selection)
            outputs.append(change_output)
        return outputs

    def assemble_transaction_spend_output(
        self,
        selection: CoinSelection,
        recipient: ExternalAddress
    ):
        return TxOut(selection.target_value, recipient.to_scriptPubKey())

    def assemble_transaction_change_output(self, selection: CoinSelection):
        if self.watch_only_wallet.last_change_address.is_fresh:
            change_address = self.watch_only_wallet.last_change_address
        else:
            change_address = self.derive_change_address()
        return TxOut(
            selection.change_value, change_address.to_scriptPubKey())


    # See https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki
    def assemble_psbt(self, transaction: Transaction, selection: CoinSelection) -> PartiallySignedTransaction:
        utxos = map_coin_selection_to_utxos(selection, self.watch_only_wallet)
        psbt = PartiallySignedTransaction(unsigned_tx=transaction)
        self.assembe_psbt_inputs(psbt, utxos)
        if len(psbt.outputs) == 2:
            self.assemble_psbt_change_output(psbt)
        return psbt


    def assembe_psbt_inputs(self, psbt: PartiallySignedTransaction, utxos: List[Utxo]):
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


    def assemble_psbt_change_output(self, psbt: PartiallySignedTransaction):
        change_output = psbt.outputs[1]
        last_change_address = self.watch_only_wallet.last_change_address
        address_derivation_info = PSBT_KeyDerivationInfo(
            self.watch_only_wallet.master_fingerprint,
            BIP32Path(last_change_address.key_path)
        )
        change_output.derivation_map[last_change_address.pub_key] = address_derivation_info






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




    # def sign_psbt(self, psbt: PartiallySignedTransaction):
    #     # lines 418 - 430 in test_psbt should get you there

    #     xpriv = ExtPrivKey("tprv8ZgxMBicQKsPehjZHpLLc55zCdP2KmM5afjfn48zmJcJAU4Jv9BcKunh8Ad5V8iHEo2juZRchVkXrRNnqq7cdNpiRsH784hzp1SWwVY7bNP")

    #     kstore = KeyStore(xpriv, require_path_templates=False)

    #     result = psbt.sign(kstore, finalize=True)

    #     print(b2x(psbt.extract_transaction().serialize()))

    #     return result.is_final and result.is_ready
