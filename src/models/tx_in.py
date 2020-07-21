from bitcointx.core import CMutableTxIn


class TxIn(CMutableTxIn):
    satoshi_value: int

    def __init__(self, satoshi_value, *args, **kwargs):
        super(TxIn, self).__init__(*args, **kwargs)
        self.satoshi_value = satoshi_value
