from typing import List

from bitcointx.core import b2x
from bitcoin_coin_selection.selection_types.input_coin import InputCoin
from bitcoin_coin_selection.selection_types.output_group import OutputGroup
from bitcoin_coin_selection.selection_types.coin_selection import CoinSelection

from bitcoin_types.utxo import Utxo
from models.watch_only_wallet import WatchOnlyWallet


def map_coin_selection_to_utxos(coin_selection: CoinSelection,
                                wallet: WatchOnlyWallet) -> List[Utxo]:
    utxos = []
    for selected_coin in coin_selection.outputs:
        address = wallet.get_address(selected_coin.address)
        utxo = next(
            filter(
                lambda tx_in: b2x(tx_in.prevout.hash) == selected_coin.tx_hash
                and tx_in.prevout.n == selected_coin.vout,  address.utxos
            )
        )
        utxos.append(utxo)
    return utxos


def map_utxos_to_output_groups(wallet: WatchOnlyWallet) -> List[OutputGroup]:
    utxo_pool = []
    for address in wallet.addresses:
        if address.utxos:
            input_coins = [
                InputCoin(
                    utxo.prevout.hash.hex(),
                    utxo.prevout.n,
                    utxo.value,
                    Utxo.spend_size(wallet.addresses[0])
                )
                for utxo in address.utxos
            ]
            utxo_pool.append(OutputGroup(str(address), input_coins))
    return utxo_pool


def get_total_effective_value(wallet: WatchOnlyWallet, fee_rate: int) -> int:
    utxo_pool = map_utxos_to_output_groups(wallet)
    for utxo in utxo_pool:
      utxo.set_fee(fee_rate, fee_rate) # long term fee doesn't matter here
    return sum(utxo.effective_value for utxo in utxo_pool)
