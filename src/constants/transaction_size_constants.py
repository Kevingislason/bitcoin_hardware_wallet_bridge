# Spend sizes (i.e. vbytes required to spend a utxo we own in the given address type)
P2PKH_SPEND_BYTES = 148
NP2WPKH_SPEND_BYTES = 110
P2WPKH_SPEND_BYTES = 68

# Output sizes (i.e. vbytes required to output a new utxo to this address type)
P2PKH_OUTPUT_BYTES = 34
NP2WPKH_OUTPUT_BYTES = 32
P2WPKH_OUTPUT_BYTES = 31

# Base transaction size independent of inputs and outputs
# i.e. Version (4b) + TxOut count (1b) + TxIn count (1b) + Lock time (4b)
TX_BASE_BYTES = 10
