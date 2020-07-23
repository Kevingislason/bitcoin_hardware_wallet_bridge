from bitcointx.core import CMutableTxIn


class TxIn(CMutableTxIn):
    satoshi_value: int

    def __init__(self, satoshi_value, *args, **kwargs):
        super(TxIn, self).__init__(*args, **kwargs)
        self.satoshi_value = satoshi_value


# class CMutableTxIn(CTxIn, mutable_of=CTxIn, next_dispatch_final=True):
    # prevout: WriteableField[CMutableOutPoint]  # type: ignore
    # scriptSig: WriteableField[script.CScript]
    # nSequence: WriteableField[int]
